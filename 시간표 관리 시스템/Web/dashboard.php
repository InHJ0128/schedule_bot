<?php
session_start();
if (!isset($_SESSION['user_id'])) {
    die("세션이 만료되었습니다. \n다시 링크로 접속해주세요.");
}
$user_id = $_SESSION['user_id'];
$user_name = $_SESSION['user_name'];
?>

<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>시간표</title>
  <link rel="stylesheet" href="dashboard.css">
</head>
<body>
<div class="title"><h2>📚</h2> <h1><?= htmlspecialchars($user_name) ?></h1> <h2> 님의 시간표</h2></div>
<div class="main_box">
    <div class="select_box">
        <div class="date_box" id="semester"></div>
        <ul class="date_list_box" id="semester_list"></ul>
        <div class="change_mod_box off" id="change_mod_box" onclick="change_mod()">수정모드 off</div>
    </div>
    <div class="change_box" id="change_box">
        <div class="create" onclick="create_schedule()">일정 추가</div>
        <div class="text">수정할 일정을 아래에 올려주세요.</div>
        <div class="edit" id="edit"></div>
        <div class="edit_list" id="edit_list">
            <div>
                <label for="name">일정 이름</lavel>
                <input class="name" id="name" type="text">
            </div>
            <div>
                <label for="professor">담당 교수</lavel>
                <input class="professor" id="professor" type="text" placeholder="생략가능">
            </div>
            <div>
                <label for="duration">일정 기간</lavel>
                <input class="duration" id="duration" type="text">
                <div>
                    <button onclick="up_duration()">^</button>
                    <button onclick="down_duration()">v</button>
                </div>
            </div>
        </div>
        <div class="text">삭제할 일정을 아래에 올려주세요.</div>
        <div class="delete" id="delete"></div>
        <div class="text"></div>
        <div class="save" onclick="save_schedule()">시간표 저장</div>
    </div>
    <table class="timetable">
    <thead>
        <tr>
        <th>시간</th>
        <th>월</th>
        <th>화</th>
        <th>수</th>
        <th>목</th>
        <th>금</th>
        </tr>
    </thead>
    <tbody>
        <?php for ($hour = 9; $hour <= 18; $hour++): ?>
        <tr>
        <th id="th-<?= $hour ?>"><?= $hour ?>시</th>
        <?php for ($day = 0; $day < 5; $day++): ?>
        <td class="cell D<?= $day ?>" id="cell-<?= $hour ?>-<?= $day ?>"></td>
        <?php endfor; ?>
        </tr>
        <?php endfor; ?>
    </tbody>
    </table>
</div>
<script>
  const user_id = <?= json_encode($user_id) ?>;
  const user_name = <?= json_encode($user_name) ?>;
</script>
<script src="dashboard.js"></script>



</body>
</html>