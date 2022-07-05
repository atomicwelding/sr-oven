clear
echo "===> Hi" $USER "! We will install sr-oven-client for you! ヽ(o＾▽＾o)ノ"

# install dependencies 
sudo apt install -y jq

# configure client_config.json
echo "===> So, let's configure client_config.json: "
while true; do
    read -p "host: " h
    read -p "port: " p
    read -p "influx_host: " ih
    read -p "influx_port: " ip
    read -p "influx_token: " it
    break
done

# save config
jq '.host |= "'$h'" | .port |= '$p' | .influx_host |= "'$ih'" | .influx_port |= "'$ip'" | .influx_token |= "'$it'"' client_config.json  >.config.tmp && cp .config.tmp client_config.json

# setup in /etc/

sudo mkdir -p /usr/local/etc/sr-oven-client
sudo cp ./client_config.json /usr/local/etc/sr-oven-client/client_config.json


tr -d '\r' <client.py >sr-oven-client
sudo cp ./sr-oven-client /usr/local/bin/sr-oven-client
sudo chmod +x /usr/local/bin/sr-oven-client


# cleaning .. 
rm ./sr-oven-client
rm ./.config.tmp


# finally
echo " ===> GG "$USER"! Sr-oven-client have been installed! Type 'sr-oven-client' in your shell!"
