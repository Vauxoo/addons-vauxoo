PATH_CERTIFICADOS=""
FILE_CER=aaa010101aaa_csd_01.cer
FILE_KEY=aaa010101aaa_csd_01.key
PASSWORD=a0123456789

cd "$PATH_CERTIFICADOS"
$PASSWORD

openssl x509  -inform DER -in "$FILE_CER" -outform PEM -pubkey -out "$FILE_CER.pem"
openssl x509 -in "$FILE_CER.pem" -serial -noout
openssl pkcs8 -inform DER -in "$FILE_KEY"                      -out "$FILE_KEY.pem"
