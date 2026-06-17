# image_lineage — 이미지 매칭/문서 계보 (격리, 현재 비활성)

이 폴더는 **5-seed judgment 데이터와 별개 계보**다. 블루프린트 이미지 자산 매칭 및
이미지 학습 매니페스트(SFT) 생성용으로, `docs/BLUEPRINT_IMAGE_*` 와 연동된다.

## 내용
- `blueprint_image_training_manifest_*.jsonl` / `*_summary.json` / `*_seed.jsonl` — 매니페스트 산출물
- `scripts/build_blueprint_sft_dataset.js` — ⚠️ 존재하지 않는 `madang_learning_core_handoff_*` 에 의존 → **현재 깨짐/비활성**
- `scripts/build_blueprint_training_manifest.js` — `docs/BLUEPRINT_IMAGE_MATCH_EVALUATION_*` 입력
- `scripts/evaluate_blueprint_curation.js` — curation 평가

## 주의
- 이 계보는 judgment 5-seed 파이프라인(`20_dataset/seeds/`)과 **섞지 않는다.**
- 스크립트들은 옛 경로(`data/blueprint`, handoff 폴더)를 참조한다. 재활성화하려면
  입력/출력 경로를 새 트리에 맞게 갱신해야 한다. (현 단계에서는 격리 보존만)
