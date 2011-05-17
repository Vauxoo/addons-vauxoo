SET FILE_CER=aaa010101aaa_csd_01.cer
SET FILE_KEY=aaa010101aaa_csd_01.key
SET PASSWORD=a0123456789

SET PATH_CERTIFICADOS=""
cd %PATH_CERTIFICADOS%

SET PATH_OPENSSL="..\..\depends_app\openssl_win"
SET path=%path%;%PATH_OPENSSL%

ECHO Cuando se le solicite teclee el password: %PASSWORD%
pause
openssl x509  -inform DER -in "%FILE_CER%" -outform PEM -pubkey -out "%FILE_CER%.pem"
openssl x509 -in "%FILE_CER%.pem" -serial -noout
openssl pkcs8 -inform DER -in "%FILE_KEY%"                      -out "%FILE_KEY%.pem"
pause