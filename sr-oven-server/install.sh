clear
echo "===> Hi" $USER "! We will install sr-oven-server for you! ヽ(o＾▽＾o)ノ"

# dependencies
pip install jsonschema flask pyvisa 

# setting up ...
sudo mkdir -p /usr/local/bin/oven 
sudo cp ./oven/config.json /usr/local/bin/oven/config.json
sudo cp ./oven/oven.py /usr/local/bin/oven/oven.py 

tr -d '\r' <server.py >sr-oven-server
sudo cp ./sr-oven-server /usr/local/bin/sr-oven-server
sudo chmod +x /usr/local/bin/sr-oven-server


# cleaning ..
sudo rm ./sr-oven-server

# finally
echo " ===> GG "$USER"! Sr-oven-server have been installed! Type 'sr-oven-server' in your shell!"

