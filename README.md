# dnd-helper


git clone .
cd dnd-helper

sudo apt install certbot

sudo certbot -d dndg.ru --manual --preferred-challenges dns certonly

add TXT record on domain provider

copy created fullchain.pem, privkey.pem to ~/certs/

docker-compose up -d
