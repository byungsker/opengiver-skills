---
name: remote-mac-folder-copy
description: 사용자가 지정한 원격 Mac에 로컬 폴더나 Skill을 SSH로 복사하고, 전송 후 체크섬으로 결과를 검증할 때 사용한다. 호스트·계정·경로를 추측하지 않는다.
---

# 원격 Mac 폴더 복사

사용자가 로컬 폴더를 지정한 원격 Mac의 경로로 옮겨 달라고 하면 이 스킬을 사용한다. 목표는 원본을 보존하면서 원격 대상 폴더를 만들고, 전송이 끝난 뒤 실제 파일 내용이 일치하는지 확인하는 것이다.

## 입력과 사전 확인

사용자가 `SOURCE_DIR`, `REMOTE_HOST`, `REMOTE_USER`, `REMOTE_DEST_DIR`, 필요 시 SSH 포트와 대상 이름을 지정해야 한다. 호스트·계정·경로가 없으면 연결을 시도하지 말고 필요한 값을 질문한다. `~`는 현재 Mac과 원격 Mac에서 각각 해석될 수 있으므로 명시적 절대 경로로 확정한다.

## Skill 공유

사용자가 Skill 공유를 명시하면 정확한 Skill 디렉터리를 확인하고, 전송할 파일 목록을 검토한다. `SKILL.md`, 필요한 `references/`·`scripts/`만 전송하며, `.env`, 키, 인증서, token, credential, 개인 설정이 있으면 중단한다. 대상 기존 파일은 삭제하지 않으며 `--delete`도 사용하지 않는다.

## 실행 절차

1. 소스 폴더가 존재하는지 확인하고, 사용자가 말한 이름이 여러 위치에 있으면 원본 경로를 명확히 한다. 원본 폴더와 원격 대상 폴더 이름이 달라도 사용자가 지정한 대상 이름을 유지한다.
2. 원격 연결과 대상 부모 폴더, 여유 공간을 먼저 확인한다.

   ```bash
   ssh -o BatchMode=yes -o ConnectTimeout=10 \
     "${REMOTE_USER}@${REMOTE_HOST}" \
     'hostname; df -h /path/to/target-parent'
   ```

3. 대상이 비어 있거나 없는 경우 `rsync`를 SSH 위에서 실행한다. 소스 경로 끝의 `/`는 폴더 자체가 아니라 폴더 안의 내용을 대상 폴더에 넣는 의미다.

   ```bash
   rsync -a --partial --stats \
     -e 'ssh -o BatchMode=yes -o ConnectTimeout=10' \
     "$SOURCE_DIR/" \
     "${REMOTE_USER}@${REMOTE_HOST}:$REMOTE_DEST_DIR/"
   ```

   `--delete`는 사용하지 않는다. 대상 폴더가 이미 있고 다른 파일을 포함할 가능성이 있으면 먼저 dry-run 결과를 확인하고, 기존 파일 덮어쓰기가 사용자 요청 범위인지 판단한다. 중단된 동일 전송을 이어가는 경우에는 같은 명령을 다시 실행할 수 있다.

4. 전송 후 체크섬 기반 dry-run을 실행한다.

   ```bash
   rsync -a --checksum --dry-run --itemize-changes --stats \
     -e 'ssh -o BatchMode=yes -o ConnectTimeout=10' \
     "$SOURCE_DIR/" \
     "${REMOTE_USER}@${REMOTE_HOST}:$REMOTE_DEST_DIR/"
   ```

   `Number of files transferred: 0`이고 itemized change가 없어야 내용 일치로 보고한다. `.DS_Store`만 차이나면 일반 `--checksum` 전송으로 해당 파일을 동기화한 뒤 dry-run을 다시 실행한다. 파일 수와 원격 경로도 함께 확인하면 좋다.

## 안전 경계

- SSH 비밀번호나 비밀값을 명령어, 로그, 결과에 출력하지 않는다. `BatchMode=yes` 인증이 실패하면 키 설정 문제로 보고하고 멈춘다.
- 사용자가 요청하지 않은 삭제, 이동, 정리, `--delete`, 광범위한 재동기화는 하지 않는다.
- Skill 자동 설치는 사용자가 원격 환경 공유를 요청한 경우에만 수행하며, Skill 번들에 포함할 파일을 먼저 검토한다.
- 대상 경로가 기존 폴더이면 덮어쓸 파일을 확인하고, 기존 자료를 훼손할 가능성이 있으면 사용자에게 한 가지 구체적인 확인을 요청한다.
- 연결 성공만으로 복사 완료라고 하지 않는다. `rsync` 종료 코드와 체크섬 검증 결과를 모두 확인한다.

## 결과 보고

최종 보고에는 소스 경로, 원격 호스트, 원격 대상 경로, 전송 결과, 체크섬 검증 결과를 간단히 남긴다. 중단·인증·용량 오류가 있으면 복사 완료로 표현하지 말고, 현재까지 확인된 상태와 필요한 조치만 보고한다.
