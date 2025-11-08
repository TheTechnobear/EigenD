# we copy and rename on EigenD, as the Scon scripts assume a flat heirarcy
# issue is, lib_pico uses the id its built with which is libpicodecoder.dylib

cp macOs/arm64/libpicodecoder.dylib ../libpico_decoder_arm64_1_0_0.dylib
install_name_tool -id @rpath/libpico_decoder_arm64_1_0_0.dylib ../libpico_decoder_arm64_1_0_0.dylib

echo ------------------------
otool -L ../libpico_decoder_arm64_1_0_0.dylib
echo ------------------------
cp macOs/x86_64/libpicodecoder.dylib ../libpico_decoder_x86_64_1_0_0.dylib
install_name_tool -id @rpath/libpico_decoder_x86_64_1_0_0.dylib ../libpico_decoder_x86_64_1_0_0.dylib
otool -L ../libpico_decoder_x86_64_1_0_0.dylib 