<?php
define("SECRET_KEY", "iwantsave");

header("Content-Type: application/json");

$mysqli = new mysqli("localhost", "inhuckjin85", "s!s30605010", "inhuckjin85"); // 
if ($mysqli->connect_errno) {
    http_response_code(500);
    echo json_encode(["success" => false, "message" => "DB 연결 실패"]);
    exit;
}

$input = json_decode(file_get_contents("php://input"), true);
if (!$input || !isset($input['user_id'], $input['user_name'], $input['semester'], $input['timetable'], $input['secret'])) {
    http_response_code(400);
    echo json_encode(["success" => false, "message" => "필수 데이터 누락"]);
    exit;
}

if ($input['secret'] !== SECRET_KEY) {
    http_response_code(403);
    echo json_encode(["success" => false, "message" => "접근 거부: secret key 불일치"]);
    exit;
}

$user_id = $input['user_id'];
$user_name = $input['user_name'];
$semester = $input['semester'];
$timetable = $input['timetable']; // 배열

$stmt = $mysqli->prepare("DELETE FROM Schedule WHERE user_id = ? AND semester = ?");
$stmt->bind_param("is", $user_id, $semester);
$stmt->execute();

$insert = $mysqli->prepare("
    INSERT INTO Schedule
    (user_id, user_name, semester, day, name, professor, room, start_time, end_time)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
");

$success_count = 0;
foreach ($timetable as $row) {
    $insert->bind_param(
        "issssssss",
        $user_id,
        $user_name,
        $semester,
        $row['day'],
        $row['name'],
        $row['professor'],
        $row['room'],
        $row['start'],
        $row['end']
    );
    if ($insert->execute()) {
        $success_count++;
    }
}

echo json_encode([
    "success" => true,
    "message" => "{$success_count}개 항목 저장 완료"
]);
?>