SET FILE_CER=aaa010101aaa_csd_01.cer
SET FILE_KEY=aaa010101aaa_csd_01.key
SET FILE_PASSWORD=password.txt

SET PATH_CERTIFICADOS=""
cd %PATH_CERTIFICADOS%

SET PATH_OPENSSL="..\..\depends_app\openssl_win"
SET path=%path%;%PATH_OPENSSL%
pause
openssl x509 -inform DER -outform PEM -in "%FILE_CER%" -pubkey -out "%FILE_CER%.pem"
openssl x509 -inform PEM -in "%FILE_CER%.pem" -serial -noout
openssl pkcs8 -inform DER -outform PEM -in "%FILE_KEY%" -passin file:"%FILE_PASSWORD%" -out "%FILE_KEY%.pem"
pause