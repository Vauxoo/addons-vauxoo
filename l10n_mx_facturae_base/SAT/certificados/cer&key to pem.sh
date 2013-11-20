PATH_CERTIFICADOS=""
FILE_CER=aaa010101aaa_csd_01.cer
FILE_KEY=aaa010101aaa_csd_01.key
FILE_PASSWORD="password.txt"

cd "$PATH_CERTIFICADOS"

openssl x509 -inform DER -in "$FILE_CER" -outform PEM -pubkey -out "$FILE_CER.pem"
openssl x509 -in "$FILE_CER.pem" -serial -noout
openssl pkcs8 -inform DER -in "$FILE_KEY" -passin file:"$FILE_PASSWORD" -out "$FILE_KEY.pem"
