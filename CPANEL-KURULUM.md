# cPanel kurulumu: Yaptığımız İşler

## İlk kurulum

1. Site dosyalarının tamamını cPanel'deki alan adının belge kök dizinine yükleyin. `portfolio-api.php`, `yaptigimiz-isler.html`, `yaptigimiz-isler.js` ve `styles.css` aynı dizinde bulunmalıdır.
2. cPanel Terminal'i açıp şu komutu çalıştırın. Komut parolayı shell geçmişine yazmaz; parola sorulduğunda güçlü ve benzersiz bir yönetici parolası girin:

   ```sh
   php -r 'fwrite(STDOUT, "Yonetici parolasi: "); $p = trim(fgets(STDIN)); echo password_hash($p, PASSWORD_DEFAULT), PHP_EOL;'
   ```

3. cPanel Dosya Yöneticisi'nde `portfolio-config.example.php` dosyasının bir kopyasını `portfolio-config.php` adıyla oluşturun. Oluşturduğunuz hash'i dosyadaki `admin_password_hash` değerinin yerine yapıştırın. Örnek dosyayı silmeyin; parola hash'i içermemelidir.
4. `data` ve `uploads/portfolio` klasörlerinin PHP tarafından yazılabilir olduğundan emin olun. API bu klasörleri gerekirse oluşturur; cPanel'in PHP işlemcisi yazma iznine sahip olmalıdır.
5. PHP 7.4 veya üzerini kullanın. PHP ayarlarında `fileinfo` ve `session` eklentilerinin açık; `upload_max_filesize` değerinin en az `20M`, `post_max_size` değerinin en az `125M`, `max_file_uploads` değerinin en az `8` olduğundan emin olun.
6. Sitenin HTTPS üzerinden açıldığını doğrulayın. Yönetici oturumu güvenli çerezleri HTTPS kullanıldığında etkinleştirir.

Ardından sitede **Yaptığımız işler** sayfasını açın ve **Yönetici girişi** düğmesinden çalışma ekleyin. Yüklenen işler ve medya dosyaları sunucuda saklanır ve ziyaretçilere hemen gösterilir. Dosya başına boyut en fazla 20 MB, çalışma başına dosya sayısı en fazla 8 ve toplam yükleme boyutu en fazla 110 MB'tır.

## Taşıma ve yedekleme

Portföy kayıtları `data/portfolio.json` içinde, görseller ve videolar `uploads/portfolio/` içinde tutulur. Siteyi taşırken veya yedeklerken her iki konumu da alın. `data` klasöründeki `.htaccess`, JSON kayıtlarının doğrudan web'den indirilmesini engeller.

Yönetici parolasını değiştirmek için yeni bir hash üretip `portfolio-config.php` içindeki `admin_password_hash` değerini güncelleyin. Bu yapılandırma dosyasını herkese açık depolara eklemeyin veya paylaşmayın.
