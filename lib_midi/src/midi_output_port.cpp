
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
#include <piw/piw_window.h>
#include <picross/pic_time.h>
#include <picross/pic_log.h>
#include <picross/pic_safeq.h>
#include <lib_midi/midi_output_port.h>
#include <lib_juce/juce.h>

#define NULL_DEVICE "None"

struct midi::midi_output_port_t::impl_t: piw::thing_t, pic::safe_worker_t
{
    impl_t(midi::midi_output_port_t *delegate_output): 
        pic::safe_worker_t(10,PIC_THREAD_PRIORITY_HIGH), current_(-1), delegate_(delegate_output),
        output_(nullptr),virtual_output_(nullptr),
        running_(false), null_device_name_(NULL_DEVICE)
    {
        piw::tsd_thing(this);
    }

    void stop()
    {
        if(running_)
        {
            running_ = false;
            cancel_timer_slow();
            quit();

            if(output_)
            {
                output_=nullptr;
            }

            if(virtual_output_)
            {
                virtual_output_=nullptr;
            }
        }
    }

    void run()
    {
        if(!running_)
        {
            running_ = true;
            pic::thread_t::run();
            timer_slow(5000);
        }
    }

    ~impl_t()
    {
        tracked_invalidate();
        stop();
    }

    void thing_timer_slow()
    {            
        scan();
    }

    void scan()
    {
        int fakeDeviceOffset = 1;
#if JUCE_MAC || JUCE_LINUX
        if(!virtual_output_ && virtual_name_.length()>0)
        {
            virtual_output_ = juce::MidiOutput::createNewDevice(virtual_name_);

            if(virtual_output_)
            {
                pic::logmsg() << "created output " << virtual_name_;
                virtualHash_ = virtual_name_.hashCode();
            }
            else
            {
                pic::logmsg() << "couldn't create output " << virtual_name_;
                virtual_name_ = ""; // don't do it again!
            }
        }
#endif


        juce::StringArray old_devices(devices_);
        juce::StringArray new_devices = juce::MidiOutput::getDevices();

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
                    if(output_) {
                        pic::logmsg() << "stop " << old_devices[0];
                        output_ = nullptr;
                    }
                    if(virtual_output_ && current_ == virtualHash_) {
                        pic::logmsg() << "stop v" << old_devices[0];
                        virtual_output_ = nullptr;
                    }
                    current_=-1;
                }
                pic::logmsg() << "sink_removed " << old_devices[0] <<  " " << old_devices[0].hashCode();
                delegate_->sink_removed(old_devices[0].hashCode());
            }
            old_devices.remove(0);
        }

        for(int i=0;i<new_devices.size();i++)
        {
            pic::logmsg() << "sink_added " << new_devices[i] <<  " " << new_devices[i].hashCode();
            delegate_->sink_added(new_devices[i].hashCode(),std::string(new_devices[i].getCharPointer()));
        }

        // are we changing devices ?
        if(selectedHash_ != current_)
        {
            // yes, stop existing device
            if(output_ ) {
                pic::logmsg() << "stopping " << current_;
                output_ = nullptr;
            }
            if(virtual_output_ && current_ == virtualHash_) 
            {
                pic::logmsg() << "stopping " << current_;
                // virtual_output_->stop(); 
            }


            current_ = selectedHash_;

            if (selectedHash_ == virtualHash_) {
                pic::logmsg() << "starting  " << virtual_name_;
            } else if (selectedHash_ == null_device_name_.hashCode()) {
                // NOP - we already stopped other inputs, dont need to start another.
                pic::logmsg() << "selected NONE  ";
            } else {
                // real device
                for(int i = fakeDeviceOffset ; i < devices_.size();i++) {
                    pic::logmsg() << i << ". " << "devices " << devices_[i] << " " << devices_[i].hashCode();
                    if(selectedHash_ == devices_[i].hashCode()) {
                        output_ =  juce::MidiOutput::openDevice(i-fakeDeviceOffset);
                        if(output_)
                        {
                            pic::logmsg() << "starting " << devices_[i] << " " << selectedHash_;
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

    static void sender__(void *a_, void *b_, void *c_, void *d_)
    {
        impl_t *self = (impl_t *)a_;
        piw::data_nb_t d = piw::data_nb_t::from_given((bct_data_t)b_);
        self->output__(d);
    }

    void output(const piw::data_nb_t &d)
    {
        add(sender__,this,d.give_copy(),0,0);
    }

    void output__(const piw::data_nb_t &d)
    {
        if(output_ || virtual_output_)
        {
            juce::MidiMessage mm((const unsigned char *)d.as_blob(),d.as_bloblen());

            if(output_)
            {
                output_->sendMessageNow(mm);
            } else if(current_ == virtualHash_)
            {
                virtual_output_->sendMessageNow(mm);
            }
        }
    }

    long get_port(void)
    {
        return current_;
    }

    bool set_port(long uid)
    {
        selectedHash_ = uid;
        scan();
        return true;
    }

    void set_source(const std::string &name)
    {
#if JUCE_MAC || JUCE_LINUX
        pic::logmsg() << "set source  : virtual output" << " name " << name;
        virtual_name_ = juce::String::fromUTF8(name.c_str());
        if(virtual_output_)
        {
            virtual_output_=nullptr;
        }
#else 
        virtual_name = "";
#endif
    }

    int current_;
    int selectedHash_ = 0;
    int virtualHash_ = 0 ;
    int nullHash_ = 0;
    juce::StringArray devices_;
    juce::String virtual_name_;
    midi::midi_output_port_t *delegate_;
    std::unique_ptr<juce::MidiOutput> output_;
    std::unique_ptr<juce::MidiOutput> virtual_output_;
    bool running_;
    juce::String null_device_name_;
};

namespace midi
{
    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------
    // midi output interface class
    //
    //
    // ------------------------------------------------------------------------------------------------------------------------------------------------------------------

    midi_output_port_t::midi_output_port_t(): impl_(new impl_t(this))
    {
    }

    long midi_output_port_t::get_port(void)
    {
        return impl_->get_port();
    }

    bool midi_output_port_t::set_port(long uid)
    {
        return impl_->set_port(uid);
    }

    void midi_output_port_t::run()
    {
        impl_->run();
    }

    void midi_output_port_t::stop()
    {
        impl_->stop();
    }

    midi_output_port_t::~midi_output_port_t()
    {
        stop();
        delete impl_;
    }

    piw::change_nb_t midi_output_port_t::get_midi_output_functor()
    {
        return piw::change_nb_t::method(impl_, &midi_output_port_t::impl_t::output);
    }

    void midi_output_port_t::set_source(const std::string &name)
    {
        impl_->set_source(name);
    }

} // namespace midi
