export JWT_PRIVATE_KEY=`cat ecdsa-p521-private.pem | base64`
export JWT_PUBLIC_KEY=`cat ecdsa-p521-public.pem | base64`

python3 __main__.py run_server
