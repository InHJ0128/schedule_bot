window.addEventListener('DOMContentLoaded', () => {
    loadTimetable(user_id, user_name,'');

    const dateBox = document.getElementById('semester');
    const listBox = document.getElementById('semester_list');
    const editBox = document.getElementById('edit');
    const deleteBox = document.getElementById('delete');

    // 클릭하면 열기/닫기
    dateBox.addEventListener('click', (e) => {
        e.stopPropagation();
        listBox.classList.toggle('show');
    });
    // 마우스가 리스트 바깥으로 나가면 닫기
    listBox.addEventListener('mouseleave', () => {
        listBox.classList.remove('show');
    });


    // 드롭 처리
    const cells = document.querySelectorAll('.cell');
    cells.forEach(cell => {
        timetable_setting(cell);
    });

    // 수정/삭제 블럭
    timetable_setting(editBox);
    timetable_setting(deleteBox);
});

function timetable_setting(cell){
    cell.addEventListener('dragover', e => e.preventDefault());

    cell.addEventListener('drop', e => {
        e.preventDefault();
        
        const id = e.dataTransfer.getData("text/plain");
        const data = document.getElementById(id);
        
        const cell_id = cell.id.split("-");
        const start = parseInt(cell_id[1],10);
        const col = parseInt(cell_id[2],10);
        const end = start + parseInt(data.dataset.duration) -1;
        const duration = parseInt(data.dataset.duration);
        const isEditMode = data.dataset.editmode === 'true';
        if (!data) return;
        //2시간 이상일때 시간표가 있으면 이동 불가
        

        if(duration > 1){
            for (let h = start + 1; h <= end; h++) {
                const checking = document.getElementById(`cell-${h.toString().padStart(2, '0')}-${col}`);
                if (!checking || checking.childElementCount == 1) return; 
            }
        }

        if(data.parentNode.id == "edit"){
            document.getElementById('edit_list').classList.remove('fade-in');
            document.getElementById('edit_list').classList.add('fade-out');
        }
        cell.appendChild(data);
        if (duration > 1 ) {
            if(!isEditMode){
        //이동전 병합된 칸 되돌리기
                const c_start = parseInt(data.dataset.start.split(":")[0]);
                const c_col = parseInt(data.dataset.day);
                data.dataset.start = start;
                data.dataset.day = col;
                console.log(`cell-${c_start.toString().padStart(2, '0')}-${c_col}`);
                console.log(document.getElementById(`cell-${c_start.toString().padStart(2, '0')}-${c_col}`));
                document.getElementById(`cell-${c_start}-${c_col}`).rowSpan = 1;
                for (let i = c_start+1; i <= c_start+duration-1; i++) {
                //td필드 생성
                    const td = document.createElement('td');
                    td.id = `cell-${i}-${c_col}`;
                    td.classList.add("cell");
                    td.classList.add("D"+c_col);
                    timetable_setting(td);
                //-------------------
                    for (let k = c_col; k<=4; k++){
                        const target = document.getElementById(`cell-${i.toString().padStart(2, '0')}-${k+1}`);
                        if(target){
                            const parent = target.parentNode;
                            parent.insertBefore(td,target);
                            break;
                        }else if(k==4){
                            const tar = document.getElementById('th-'+i);
                            const parent = tar.parentNode;
                            parent.appendChild(td);
                            break;
                        }
                    }
                }
            }
        //이동후 칸 병합하기
            if(data.parentNode.id == "edit"){
                document.getElementById('edit_list').classList.add('fade-in');
                document.getElementById('edit_list').classList.remove('fade-out');
                data.dataset.editmode = true;
            }else{
                cell.rowSpan = duration;
                for (let h = start + 1; h <= end; h++) {
                    const removeCell = document.getElementById(`cell-${h.toString().padStart(2, '0')}-${col}`);
                    if (removeCell) removeCell.remove();
                }
            }
            if(isEditMode) data.dataset.editmode = false;
        }
    });
}


const dayIndex = { "월": 0, "화": 1, "수": 2, "목": 3, "금": 4 };

function trimTime(timeStr) {
    return timeStr.slice(0, 5); // 14:00:00 → 14:00
}
function loadTimetable(user_id, user_name, semester){
    fetch('/python/load_schedule.php', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        secret: 'iwantload',
        semester: semester,  // 비워두면 최신 학기 자동 처리
        user_id: user_id,
        user_name: user_name,
        semester_check: true
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.timetable.length > 0) {
            const sm = document.getElementById('semester');
            sm.textContent = data.time;
            data.timetable.forEach(item => {
                const start = parseInt(item.start_time.slice(0, 2), 10);
                const end = parseInt(item.end_time.slice(0, 2), 10);
                const duration = end - start;
                const col = dayIndex[item.day];
                // 시작 셀에 내용 + rowspan 부여
                const cell = document.getElementById(`cell-${start.toString().padStart(2, '0')}-${col}`);
                if (cell) {
                    cell.rowSpan = duration;
                // 아래 시간대 셀 제거
                    for (let h = start + 1; h < end; h++) {
                        const removeCell = document.getElementById(`cell-${h.toString().padStart(2, '0')}-${col}`);
                        if (removeCell) removeCell.remove();
                    }
                //수업 블럭
                    const subject = document.createElement('div');
                    subject.classList.add("subject");
                    subject.innerHTML = `${item.name}<br><small>(${item.professor})</small>`;
                    subject.dataset.duration = duration;
                    subject.dataset.start = item.start_time;
                    subject.dataset.day = dayIndex[item.day];
                    subject.dataset.editmode = false;
                    subject.draggable = "true";
                    subject.classList.add("false")
                    subject.id = "subject"+item.name

                    subject.addEventListener('dragstart', e => {
                        if(e.target.classList.contains("false")){
                            e.preventDefault(); // 드래그 막기6
                            return;
                        }
                        const duration = parseInt(e.target.dataset.duration);
                        const start = parseInt(e.target.dataset.start);
                        const col = e.target.dataset.day;
                        const id = e.target.id;
                        
                        e.dataTransfer.setData("text/plain", id);

                        
                    });
                    cell.appendChild(subject); 
                }
            });
        } else {
            alert("\n시간표 정보를 불러올 수 없습니다.\n"+ JSON.stringify(data));
        }

        if (data.success && data.semester.length > 0) {
            const list = document.getElementById('semester_list');
            list.innerHTML = '';
            data.semester.forEach(item => {
                const li = document.createElement('li');
                
                li.classList.add('semesters');
                if ( data.time == item) li.classList.add('selected');
                li.innerHTML = `${item}`;
                li.addEventListener('click', () => {
                    // 기존 선택 제거
                    document.querySelectorAll('.semesters.selected').forEach(el => {
                        el.classList.remove('selected');
                    });
                    // 현재 선택 추가
                    li.classList.add('selected');
                
                    // 여기에 학기 선택 후 시간표 다시 불러오기 등의 로직 추가 가능
                    loadTimetable(user_id, user_name, item); // 예시
                  });
                list.appendChild(li);
            });
        }
    });
}

function change_mod(){
    const item = document.getElementById("change_mod_box");
    const table = document.getElementById("change_box");
    if(item.classList.contains("off")){
        item.classList.remove('off');
        item.classList.add('on');
        item.innerText = "수정모드 on";
        table.classList.toggle('show');
        const subjects = document.querySelectorAll('.subject');
        subjects.forEach(sub => {
            sub.classList.remove("false");
            sub.classList.add("true");
        });
    } else {
        item.classList.remove('on');
        item.classList.add('off');
        item.innerText = "수정모드 off";
        table.classList.remove('show');
        const subjects = document.querySelectorAll('.subject');
        subjects.forEach(sub => {
            sub.classList.remove("true");
            sub.classList.add("false");
        });
    }
}