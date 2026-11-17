<?php
declare(strict_types=1);

const PORTFOLIO_FORMAT = 'oh-temizlik-portfolio';
const PORTFOLIO_VERSION = 1;
const MAX_MEDIA_FILES = 8;
const MAX_MEDIA_BYTES = 20971520;
const MAX_TOTAL_MEDIA_BYTES = 115343360;
const MAX_REQUEST_BYTES = 125829120;

function ensureDirectoryRules(string $directory, string $rules): void
{
    $path = $directory . DIRECTORY_SEPARATOR . '.htaccess';
    if (is_file($path)) {
        return;
    }

    $file = fopen($path, 'x');
    if ($file === false) {
        if (is_file($path)) {
            return;
        }
        throw new RuntimeException('Klasör erişim kuralları oluşturulamadı.');
    }
    $written = fwrite($file, $rules);
    $flushed = $written === strlen($rules) && fflush($file);
    fclose($file);
    if (!$flushed) {
        unlink($path);
        throw new RuntimeException('Klasör erişim kuralları kaydedilemedi.');
    }
}

final class ApiException extends RuntimeException
{
    public int $status;

    public function __construct(int $status, string $message)
    {
        parent::__construct($message);
        $this->status = $status;
    }
}

function respond(int $status, array $payload): void
{
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store, private');
    echo json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

function ensureDataDirectory(): string
{
    $directory = __DIR__ . DIRECTORY_SEPARATOR . 'data';
    if (!is_dir($directory) && !mkdir($directory, 0755, true) && !is_dir($directory)) {
        throw new RuntimeException('Veri klasörü oluşturulamadı.');
    }
    ensureDirectoryRules($directory, "Require all denied\n");
    return $directory;
}

function validateStore($store): array
{
    if (
        !is_array($store)
        || ($store['format'] ?? null) !== PORTFOLIO_FORMAT
        || ($store['version'] ?? null) !== PORTFOLIO_VERSION
        || !isset($store['works'])
        || !is_array($store['works'])
    ) {
        throw new RuntimeException('Portföy verisi tanınmıyor veya bozuk; dosyanın üzerine yazılmadı.');
    }

    foreach ($store['works'] as $work) {
        if (
            !is_array($work)
            || !is_string($work['id'] ?? null)
            || !preg_match('/^[a-f0-9]{16}$/', $work['id'])
            || !is_string($work['title'] ?? null)
            || $work['title'] === ''
            || strlen($work['title']) > 400
            || !is_string($work['category'] ?? null)
            || $work['category'] === ''
            || strlen($work['category']) > 160
            || !is_string($work['description'] ?? null)
            || $work['description'] === ''
            || strlen($work['description']) > 3200
            || !is_string($work['createdAt'] ?? null)
            || strtotime($work['createdAt']) === false
            || !is_array($work['media'] ?? null)
            || count($work['media']) < 1
            || count($work['media']) > MAX_MEDIA_FILES
        ) {
            throw new RuntimeException('Portföy kaydı tanınmıyor veya bozuk; dosyanın üzerine yazılmadı.');
        }

        foreach ($work['media'] as $media) {
            if (
                !is_array($media)
                || !in_array($media['type'] ?? null, ['image', 'video'], true)
                || !is_string($media['url'] ?? null)
                || !preg_match('~^uploads/portfolio/[a-f0-9]{32}\.(jpg|png|webp|mp4|webm)$~', $media['url'])
                || !is_int($media['size'] ?? null)
                || $media['size'] < 1
                || $media['size'] > MAX_MEDIA_BYTES
            ) {
                throw new RuntimeException('Portföy medya kaydı tanınmıyor veya bozuk; dosyanın üzerine yazılmadı.');
            }
        }
    }

    return $store['works'];
}

function readStoreUnlocked(string $directory): array
{
    $path = $directory . DIRECTORY_SEPARATOR . 'portfolio.json';
    if (!is_file($path)) {
        return [];
    }

    $contents = file_get_contents($path);
    if ($contents === false) {
        throw new RuntimeException('Portföy verisi okunamadı.');
    }

    try {
        $store = json_decode($contents, true, 512, JSON_THROW_ON_ERROR);
    } catch (JsonException $exception) {
        throw new RuntimeException('Portföy verisi bozuk; dosyanın üzerine yazılmadı.', 0, $exception);
    }

    return validateStore($store);
}

function atomicWriteStore(string $directory, array $works): void
{
    $path = $directory . DIRECTORY_SEPARATOR . 'portfolio.json';
    $temporaryPath = $directory . DIRECTORY_SEPARATOR . 'portfolio.' . bin2hex(random_bytes(8)) . '.tmp';
    $contents = json_encode(
        ['format' => PORTFOLIO_FORMAT, 'version' => PORTFOLIO_VERSION, 'works' => $works],
        JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR
    );
    $file = fopen($temporaryPath, 'xb');
    if ($file === false) {
        throw new RuntimeException('Geçici portföy dosyası oluşturulamadı.');
    }

    try {
        $offset = 0;
        $length = strlen($contents);
        while ($offset < $length) {
            $written = fwrite($file, substr($contents, $offset));
            if ($written === false || $written === 0) {
                throw new RuntimeException('Portföy verisi yazılamadı.');
            }
            $offset += $written;
        }
        if (!fflush($file)) {
            throw new RuntimeException('Portföy verisi diske aktarılamadı.');
        }
    } catch (Throwable $exception) {
        fclose($file);
        unlink($temporaryPath);
        throw $exception;
    }
    fclose($file);

    if (!rename($temporaryPath, $path)) {
        unlink($temporaryPath);
        throw new RuntimeException('Portföy verisi güvenli biçimde güncellenemedi.');
    }
}

function readWorks(): array
{
    $directory = ensureDataDirectory();
    $lock = fopen($directory . DIRECTORY_SEPARATOR . 'portfolio.lock', 'c+');
    if ($lock === false) {
        throw new RuntimeException('Portföy kilit dosyası açılamadı.');
    }
    try {
        if (!flock($lock, LOCK_SH)) {
            throw new RuntimeException('Portföy verisi kilitlenemedi.');
        }
        return readStoreUnlocked($directory);
    } finally {
        flock($lock, LOCK_UN);
        fclose($lock);
    }
}

function updateWorks(callable $update): array
{
    $directory = ensureDataDirectory();
    $lock = fopen($directory . DIRECTORY_SEPARATOR . 'portfolio.lock', 'c+');
    if ($lock === false) {
        throw new RuntimeException('Portföy kilit dosyası açılamadı.');
    }
    try {
        if (!flock($lock, LOCK_EX)) {
            throw new RuntimeException('Portföy verisi kilitlenemedi.');
        }
        $works = readStoreUnlocked($directory);
        $works = $update($works);
        if (!is_array($works)) {
            throw new RuntimeException('Portföy güncellemesi geçersiz veri üretti.');
        }
        atomicWriteStore($directory, $works);
        return $works;
    } finally {
        flock($lock, LOCK_UN);
        fclose($lock);
    }
}

function startAdminSession(): void
{
    if (session_status() === PHP_SESSION_ACTIVE) {
        return;
    }

    session_set_cookie_params([
        'lifetime' => 0,
        'path' => '/',
        'secure' => isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== '' && $_SERVER['HTTPS'] !== 'off',
        'httponly' => true,
        'samesite' => 'Strict',
    ]);
    if (!session_start()) {
        throw new RuntimeException('Yönetici oturumu başlatılamadı.');
    }
    if (!isset($_SESSION['csrf_token']) || !is_string($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
}

function readJsonBody(): array
{
    $contents = file_get_contents('php://input');
    if ($contents === false || strlen($contents) > 16384) {
        throw new ApiException(413, 'İstek boyutu izin verilen sınırı aşıyor.');
    }
    try {
        $body = json_decode($contents, true, 32, JSON_THROW_ON_ERROR);
    } catch (JsonException $exception) {
        throw new ApiException(400, 'İstek verisi geçerli JSON değil.');
    }
    if (!is_array($body)) {
        throw new ApiException(400, 'İstek verisi geçersiz.');
    }
    return $body;
}

function requireCsrfToken($providedToken): void
{
    if (
        !is_string($providedToken)
        || !isset($_SESSION['csrf_token'])
        || !is_string($_SESSION['csrf_token'])
        || !hash_equals($_SESSION['csrf_token'], $providedToken)
    ) {
        throw new ApiException(403, 'Oturum doğrulaması başarısız. Sayfayı yenileyip tekrar deneyin.');
    }
}

function requireAdmin(): void
{
    if (($_SESSION['authenticated'] ?? false) !== true) {
        throw new ApiException(401, 'Devam etmek için yönetici girişi yapın.');
    }
}

function readPasswordHash(): string
{
    $configPath = __DIR__ . DIRECTORY_SEPARATOR . 'portfolio-config.php';
    if (!is_file($configPath)) {
        throw new ApiException(503, 'Yönetici parolası henüz ayarlanmamış. cPanel kurulum adımlarını tamamlayın.');
    }
    $config = require $configPath;
    if (!is_array($config) || !is_string($config['admin_password_hash'] ?? null) || $config['admin_password_hash'] === '') {
        throw new RuntimeException('Yönetici parola ayarı geçersiz.');
    }
    return $config['admin_password_hash'];
}

function validateText($value, string $field, int $maxLength): string
{
    if (!is_string($value)) {
        throw new ApiException(400, $field . ' alanı zorunludur.');
    }
    $value = trim($value);
    if ($value === '' || strlen($value) > $maxLength * 4 || preg_match('//u', $value) !== 1) {
        throw new ApiException(400, $field . ' alanını kontrol edin.');
    }
    $length = function_exists('mb_strlen') ? mb_strlen($value, 'UTF-8') : strlen($value);
    if ($length > $maxLength) {
        throw new ApiException(400, $field . ' en fazla ' . $maxLength . ' karakter olabilir.');
    }
    return $value;
}

function normalizeMediaUploads(): array
{
    if (!isset($_FILES['media']) || !is_array($_FILES['media']['name'] ?? null)) {
        throw new ApiException(400, 'En az bir fotoğraf veya video seçin.');
    }
    $files = $_FILES['media'];
    $count = count($files['name']);
    if ($count < 1 || $count > MAX_MEDIA_FILES) {
        throw new ApiException(400, 'Bir çalışma için en fazla ' . MAX_MEDIA_FILES . ' dosya yükleyebilirsiniz.');
    }

    $allowedTypes = [
        'image/jpeg' => ['type' => 'image', 'extension' => 'jpg'],
        'image/png' => ['type' => 'image', 'extension' => 'png'],
        'image/webp' => ['type' => 'image', 'extension' => 'webp'],
        'video/mp4' => ['type' => 'video', 'extension' => 'mp4'],
        'video/webm' => ['type' => 'video', 'extension' => 'webm'],
    ];
    $normalized = [];
    $totalBytes = 0;
    $finfo = new finfo(FILEINFO_MIME_TYPE);

    for ($index = 0; $index < $count; $index++) {
        $error = $files['error'][$index] ?? UPLOAD_ERR_NO_FILE;
        if ($error !== UPLOAD_ERR_OK) {
            if ($error === UPLOAD_ERR_INI_SIZE || $error === UPLOAD_ERR_FORM_SIZE) {
                throw new ApiException(413, 'Bir dosya sunucunun yükleme sınırını aştı.');
            }
            throw new ApiException(400, 'Dosyalardan biri yüklenemedi. Yeniden seçip deneyin.');
        }
        $temporaryPath = $files['tmp_name'][$index] ?? '';
        $size = (int) ($files['size'][$index] ?? 0);
        if (!is_string($temporaryPath) || !is_uploaded_file($temporaryPath) || $size < 1) {
            throw new ApiException(400, 'Yüklenen dosya geçersiz.');
        }
        if ($size > MAX_MEDIA_BYTES) {
            throw new ApiException(413, 'Her fotoğraf veya video en fazla 20 MB olabilir.');
        }
        $totalBytes += $size;
        if ($totalBytes > MAX_TOTAL_MEDIA_BYTES) {
            throw new ApiException(413, 'Bir çalışma için toplam dosya boyutu 110 MB sınırını aşıyor.');
        }

        $mime = $finfo->file($temporaryPath);
        if (!is_string($mime) || !isset($allowedTypes[$mime])) {
            throw new ApiException(400, 'Yalnızca JPG, PNG, WebP, MP4 ve WebM dosyaları yüklenebilir.');
        }
        $normalized[] = [
            'temporaryPath' => $temporaryPath,
            'type' => $allowedTypes[$mime]['type'],
            'extension' => $allowedTypes[$mime]['extension'],
            'size' => $size,
        ];
    }

    return $normalized;
}

function uploadDirectory(): string
{
    $directory = __DIR__ . DIRECTORY_SEPARATOR . 'uploads' . DIRECTORY_SEPARATOR . 'portfolio';
    if (!is_dir($directory) && !mkdir($directory, 0755, true) && !is_dir($directory)) {
        throw new RuntimeException('Medya klasörü oluşturulamadı.');
    }
    ensureDirectoryRules($directory, "Options -Indexes\n<FilesMatch \"\\.(php[0-9]?|phtml|phar)$\">\n  Require all denied\n</FilesMatch>\n");
    return $directory;
}

function removeSavedFiles(array $urls): bool
{
    $directory = uploadDirectory();
    $allRemoved = true;
    foreach ($urls as $url) {
        $filename = basename($url);
        if (!preg_match('/^[a-f0-9]{32}\.(jpg|png|webp|mp4|webm)$/', $filename)) {
            continue;
        }
        $path = $directory . DIRECTORY_SEPARATOR . $filename;
        if (is_file($path) && !unlink($path)) {
            error_log('OH Temizlik portföy dosyası silinemedi: ' . $filename);
            $allRemoved = false;
        }
    }
    return $allRemoved;
}

function requireMethod(string $method): void
{
    if (($_SERVER['REQUEST_METHOD'] ?? '') !== $method) {
        header('Allow: ' . $method);
        throw new ApiException(405, 'Bu işlem için HTTP ' . $method . ' yöntemi kullanılmalı.');
    }
}

header('X-Content-Type-Options: nosniff');
header('Referrer-Policy: strict-origin-when-cross-origin');

try {
    $action = $_GET['action'] ?? '';
    if (!is_string($action)) {
        throw new ApiException(400, 'İşlem adı geçersiz.');
    }

    if ($action === 'works') {
        requireMethod('GET');
        respond(200, ['ok' => true, 'works' => readWorks()]);
    }

    if ($action === 'session') {
        requireMethod('GET');
        startAdminSession();
        respond(200, [
            'ok' => true,
            'authenticated' => ($_SESSION['authenticated'] ?? false) === true,
            'csrfToken' => $_SESSION['csrf_token'],
        ]);
    }

    startAdminSession();

    if ($action === 'login') {
        requireMethod('POST');
        $body = readJsonBody();
        requireCsrfToken($body['csrfToken'] ?? null);
        $now = time();
        $attempts = array_values(array_filter(
            $_SESSION['login_attempts'] ?? [],
            static fn($attempt): bool => is_int($attempt) && $attempt > $now - 900
        ));
        if (count($attempts) >= 5) {
            throw new ApiException(429, 'Çok fazla hatalı giriş denemesi. 15 dakika sonra tekrar deneyin.');
        }
        $password = $body['password'] ?? null;
        if (!is_string($password) || strlen($password) > 1024 || !password_verify($password, readPasswordHash())) {
            $attempts[] = $now;
            $_SESSION['login_attempts'] = $attempts;
            throw new ApiException(401, 'Parola hatalı.');
        }
        session_regenerate_id(true);
        $_SESSION['authenticated'] = true;
        $_SESSION['login_attempts'] = [];
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
        respond(200, ['ok' => true, 'csrfToken' => $_SESSION['csrf_token']]);
    }

    if ($action === 'logout') {
        requireMethod('POST');
        $body = readJsonBody();
        requireCsrfToken($body['csrfToken'] ?? null);
        unset($_SESSION['authenticated']);
        session_regenerate_id(true);
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
        respond(200, ['ok' => true, 'csrfToken' => $_SESSION['csrf_token']]);
    }

    if ($action === 'create') {
        requireMethod('POST');
        requireAdmin();
        if ((int) ($_SERVER['CONTENT_LENGTH'] ?? 0) > MAX_REQUEST_BYTES) {
            throw new ApiException(413, 'İstek boyutu izin verilen 120 MB sınırını aşıyor.');
        }
        requireCsrfToken($_POST['csrfToken'] ?? null);
        $title = validateText($_POST['title'] ?? null, 'İş başlığı', 100);
        $category = validateText($_POST['category'] ?? null, 'Kategori', 40);
        $description = validateText($_POST['description'] ?? null, 'Açıklama', 800);
        $uploads = normalizeMediaUploads();
        $directory = uploadDirectory();
        $media = [];
        $savedUrls = [];

        try {
            foreach ($uploads as $upload) {
                $filename = bin2hex(random_bytes(16)) . '.' . $upload['extension'];
                $destination = $directory . DIRECTORY_SEPARATOR . $filename;
                if (!move_uploaded_file($upload['temporaryPath'], $destination)) {
                    throw new RuntimeException('Yüklenen medya dosyası kaydedilemedi.');
                }
                $url = 'uploads/portfolio/' . $filename;
                $savedUrls[] = $url;
                $media[] = [
                    'type' => $upload['type'],
                    'url' => $url,
                    'size' => $upload['size'],
                ];
            }

            $work = [
                'id' => bin2hex(random_bytes(8)),
                'title' => $title,
                'category' => $category,
                'description' => $description,
                'createdAt' => date(DATE_ATOM),
                'media' => $media,
            ];
            $works = updateWorks(static function (array $works) use ($work): array {
                array_unshift($works, $work);
                return $works;
            });
        } catch (Throwable $exception) {
            removeSavedFiles($savedUrls);
            throw $exception;
        }

        respond(201, ['ok' => true, 'csrfToken' => $_SESSION['csrf_token'], 'works' => $works]);
    }

    if ($action === 'delete') {
        requireMethod('POST');
        requireAdmin();
        $body = readJsonBody();
        requireCsrfToken($body['csrfToken'] ?? null);
        $id = $body['id'] ?? null;
        if (!is_string($id) || !preg_match('/^[a-f0-9]{16}$/', $id)) {
            throw new ApiException(400, 'Kaldırılacak çalışma seçimi geçersiz.');
        }
        $removed = null;
        $works = updateWorks(static function (array $works) use ($id, &$removed): array {
            foreach ($works as $index => $work) {
                if ($work['id'] === $id) {
                    $removed = $work;
                    array_splice($works, $index, 1);
                    break;
                }
            }
            if ($removed === null) {
                throw new ApiException(404, 'Bu çalışma bulunamadı.');
            }
            return $works;
        });
        if (!removeSavedFiles(array_column($removed['media'], 'url'))) {
            throw new RuntimeException('Çalışma kaldırıldı ancak medya dosyalarından bazıları silinemedi.');
        }
        respond(200, ['ok' => true, 'csrfToken' => $_SESSION['csrf_token'], 'works' => $works]);
    }

    throw new ApiException(404, 'İstenen işlem bulunamadı.');
} catch (ApiException $exception) {
    respond($exception->status, ['ok' => false, 'error' => $exception->getMessage()]);
} catch (Throwable $exception) {
    error_log('OH Temizlik portföy API hatası: ' . $exception->getMessage());
    respond(500, ['ok' => false, 'error' => 'İşlem tamamlanamadı. Sunucu günlüklerini kontrol edin.']);
}
