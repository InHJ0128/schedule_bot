<?php
define("SECRET_KEY", "iwantdelete");
header("Content-Type: application/json");

$mysqli = new mysqli("localhost", "inhuckjin85", "s!s30605010", "inhuckjin85");
if ($mysqli->connect_errno) {
    http_response_code(500);
    echo json_encode(["success" => false, "message" => "DB 연결 실패"]);
    exit;
}

$input = json_decode(file_get_contents("php://input"), true);

if (!$input || !isset($input['semester'], $input['secret'])) {
    http_response_code(400);
    echo json_encode(["success" => false, "message" => "필수 항목 누락"]);
    exit;
}

$semester = $input['semester'];
$secret = $input['secret'];
$user_id = $input['user_id'] ?? null;

if ($secret !== SECRET_KEY) {
    http_response_code(403);
    echo json_encode(["success" => false, "message" => "비밀키 오류"]);
    exit;
}

$stmt = $mysqli->prepare("DELETE FROM Schedule WHERE user_id = ? AND semester = ?");
$stmt->bind_param("is", $user_id, $semester);
$stmt->execute();




echo json_encode([
    "success" => true,
    "message" => "삭제 완료"
]);
?>