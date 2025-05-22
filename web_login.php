<?php
define("SECRET_KEY", "createSite");

$token = $_GET['token'] ?? '';
$decoded = base64_decode($token);

if (!$decoded || substr_count($decoded, ':') < 3) {
    die("base64 디코딩 실패: " . htmlspecialchars($token));
    //die("잘못된 토큰입니다.");
}
list($uid, $ts, $sig, $uname) = explode(':', $decoded, 4);

// 검증용 시그니처 생성
$expected = hash_hmac('sha256', "$uid:$ts", SECRET_KEY);
if (!hash_equals($expected, $sig)) {
    die("서명 위조되었습니다.");
}
if (time() - (int)$ts > 300) {
    die("만료된 링크입니다.");
}

// 로그인 처리 진행
session_start();
$_SESSION['user_id'] = $uid;
$_SESSION['user_name'] = urldecode($uname);
header("Location: /schedule/dashboard.php");
exit;
?>