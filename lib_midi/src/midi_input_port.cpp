
/*
 Copyright 2009 Eigenlabs Ltd.  http://www.eigenlabs.com

 This file is part of EigenD.

 EigenD is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 EigenD is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with EigenD.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <piw/piw_tsd.h>
#include <piw/piw_thing.h>
#include <piw/piw_fastdata.h>
#include <piw/piw_bundle.h>

#include <picross/pic_time.h>
#include <picross/pic_log.h>
#include <picross/pic_config.h>

#include <lib_midi/midi_input_port.h>

#include <lib_juce/juce.h>

#include <iostream>
#include <iomanip>

using namespace std;

#define MIDI_INPUT_DEBUG 0

// number of MIDI keys on keyboard
#define KEYS 128
#define KBD_LATENCY 5000
#define NULL_DEVICE "None"

struct midi::midi_input_port_t::impl_t: piw::thing_t, juce::MidiInputCallback
{
    impl_t(midi::midi_input_port_t *d,const piw::change_nb_t &r): 
        current_(-1), receiver_(r), delegate_(d), input_(nullptr), virtual_input_(nullptr), running_(false), null_device_name_(NULL_DEVICE)
    {
        snapshot_.save();
        piw::tsd_thing(this);
    }

    ~impl_t()
    {
        tracked_invalidate();
        stop();
    }

    void run()
    {
        if(!running_)
        {
            running_ = true;
            timer_slow(2000);
        }
    }

    void stop()
    {
        if(running_)
        {
            running_= false;
            cancel_timer_slow();


            if(input_)
            {
                input_->stop();
                input_ = nullptr;
            }
            if(virtual_input_) {
                if(current_ == virtualHash_) {
                    virtual_input_->stop();
                }
                virtual_input_ = nullptr;
            }
        }
    }

    void thing_dequeue_fast(const piw::data_nb_t &d)
    {
        receiver_(d);
    }

    void handleIncomingMidiMessage(juce::MidiInput* source, const juce::MidiMessage& message)
    {
        snapshot_.install();

        try
        {            
            unsigned char *output_buffer;
            piw::data_nb_t midi_data = piw::makeblob_nb(0, message.getRawDataSize(), &output_buffer);
            memcpy(output_buffer, message.getRawData(), message.getRawDataSize());
            enqueue_fast(midi_data);
        }
        CATCHLOG()
    }

    bool set_port(int uid)
    {
        selectedHash_ = uid;
        scan();
        return true;
    }

    long get_port()
    {
        return current_;
    }

    void thing_timer_slow()
    {
        scan();
    }

    void scan()
    {
        int fakeDeviceOffset = 1;
#if JUCE_MAC || JUCE_LINUX

        if(!virtual_input_ && virtual_name_.length()>0)
        {
            virtual_input_ = juce::MidiInput::createNewDevice(virtual_name_,this);
            if(virtual_input_)
            {
                pic::logmsg() << "created input " << virtual_name_;
                virtualHash_ = virtual_name_.hashCode();
            }
            else
            {
                pic::logmsg() << "couldn't create input " << virtual_name_;
                virtual_name_ = "";
            }
        }
#endif

        juce::StringArray old_devices(devices_);
        juce::StringArray new_devices = juce::MidiInput::getDevices();

        if(virtual_name_.length() > 0) {
            new_devices.insert(0,virtual_name_);
            fakeDeviceOffset++;
        }
        new_devices.insert(0,null_device_name_);
        devices_ = new_devices;

        while(old_devices.size()>0)
        {
            int si = new_devices.indexOf(old_devices[0]);

            if(si>=0)
            {
                new_devices.remove(si);
            }
            else
            {
                if(old_devices[0].hashCode() == current_) {
                    if(input_) {
                        pic::logmsg() << "stop " << old_devices[0];
                        input_->stop();
                        input_=nullptr;
                    }
                    if(virtual_input_&& current_ == virtualHash_) {
                        pic::logmsg() << "stop v" << old_devices[0];
                        virtual_input_->stop();
                        virtual_input_=nullptr;
                    }
                    current_=-1;
                }
                pic::logmsg() << "source_removed " << old_devices[0] <<  " " << old_devices[0].hashCode();
                delegate_->source_removed(old_devices[0].hashCode());
            }
            old_devices.remove(0);
        }

        for(int i=0;i<new_devices.size();i++)
        {
            pic::logmsg() << "source_added " << new_devices[i] <<  " " << new_devices[i].hashCode();
            delegate_->source_added(new_devices[i].hashCode(),std::string(new_devices[i].getCharPointer()));
        }

        // are we changing devices ?
        if(selectedHash_ != current_)
        {
            // yes, stop existing device
            if(input_ ) {
                pic::logmsg() << "stopping " << current_;
                input_->stop();
                input_ = nullptr;
            }
            if(virtual_input_ && current_ == virtualHash_) 
            {
                pic::logmsg() << "stopping " << current_;
                virtual_input_->stop();
            }


            current_ = selectedHash_;

            if (selectedHash_ == virtualHash_) {
                pic::logmsg() << "starting  " << virtual_name_;
                virtual_input_->start();
            } else if (selectedHash_ == null_device_name_.hashCode()) {
                // NOP - we already stopped other inputs, dont need to start another.
                pic::logmsg() << "selected NONE  ";
            } else {
                // real device
                for(int i = fakeDeviceOffset ; i < devices_.size();i++) {
                    if(selectedHash_ == devices_[i].hashCode()) {
                        input_ = juce::MidiInput::openDevice(i-fakeDeviceOffset,this);                    
                        if(input_)
                        {
                            pic::logmsg() << "starting " << devices_[i] << " " << selectedHash_;
                            input_->start();
                        }
                        else
                        {
                            pic::logmsg() << "could not open " << devices_[i];
                        }
                    }
                }
            }
       }
    }



    void set_destination(const std::string &name)
    {
#if JUCE_MAC || JUCE_LINUX
        pic::logmsg() << "set destination  : virtual input" << " name " << name;
        virtual_name_ = juce::String::fromUTF8(name.c_str());
        if(virtual_input_)
        {
            virtual_input_->stop();
            virtual_input_=nullptr;
        }
#else 
        virtual_name = "";
#endif
    }

    int current_ = 0;
    int selectedHash_ = 0;
    int virtualHash_ = 0 ;
    int nullHash_ = 0;
    juce::StringArray devices_;
    piw::change_nb_t receiver_;
    midi::midi_input_port_t *delegate_;
    std::unique_ptr<juce::MidiInput> input_;
    std::unique_ptr<juce::MidiInput> virtual_input_;
    juce::String virtual_name_;
    piw::tsd_snapshot_t snapshot_;
    bool running_;
    juce::String null_device_name_;
};

midi::midi_input_port_t::midi_input_port_t(const piw::change_nb_t &sink) { impl_ = new impl_t(this,sink); }
midi::midi_input_port_t::~midi_input_port_t() { stop(); delete impl_; }
bool midi::midi_input_port_t::set_port(long port) { return impl_->set_port(port); }
long midi::midi_input_port_t::get_port(void) { return impl_->get_port(); }
void midi::midi_input_port_t::set_destination(const std::string &name) { impl_->set_destination(name); }
void midi::midi_input_port_t::run() { return impl_->run(); }
void midi::midi_input_port_t::stop() { return impl_->stop(); }
