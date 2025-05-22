<?php
define("SECRET_KEY", "iwantload");
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

$semester = $input['semester'] ?: getCurrentSemester();
$secret = $input['secret'];
$user_id = $input['user_id'] ?? null;
$user_name = $input['user_name'] ?? null;
$semester_check = $input['semester_check'] ?? false;

if ($secret !== SECRET_KEY) {
    http_response_code(403);
    echo json_encode(["success" => false, "message" => "비밀키 오류"]);
    exit;
}

$query = "SELECT * FROM Schedule WHERE semester = ?";
$params = [$semester];

if ($user_id) {
    $query .= " AND user_id = ?";
    $params[] = $user_id;
} elseif ($user_name) {
    $query .= " AND user_name = ?";
    $params[] = $user_name;
}

$stmt = $mysqli->prepare($query);
$types = str_repeat("s", count($params));
$stmt->bind_param($types, ...$params);
$stmt->execute();
$result = $stmt->get_result();

$schedule = [];
while ($row = $result->fetch_assoc()) {
    $schedule[] = $row;
}

$semesters = [];
if ($semester_check){
    $stmt = $mysqli->prepare("SELECT DISTINCT semester FROM Schedule WHERE user_id = ?");
    $stmt->bind_param("i", $user_id);
    $stmt->execute();
    $result = $stmt->get_result();
    
    while ($row = $result->fetch_assoc()) {
        $semesters[] = $row['semester'];
    }
}
echo json_encode(["success" => true, "timetable" => $schedule, "time"=>$semester, "semester"=>$semesters] );

function getCurrentSemester() {
    $year = date("Y");
    $month = (int)date("m");
    return $year . '년' . ($month <= 7 ? '1학기' : '2학기');
}
?>