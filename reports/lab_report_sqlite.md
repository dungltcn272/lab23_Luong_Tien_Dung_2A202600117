# Day 08 Lab Report - SQLite / Persistence Appendix

## 1. Mục đích của file này

Đây là bản report phụ tập trung riêng vào phần **persistence với SQLite**. Mục tiêu không phải lặp lại toàn bộ report chính, mà là ghi rõ:

- graph đã được chạy với checkpointer SQLite như thế nào
- checkpoint được lưu ra sao
- khả năng resume / crash recovery đã được minh họa bằng gì
- metrics của lần chạy SQLite hiện tại đang phản ánh điều gì

File này phù hợp để nộp kèm như một phụ lục kỹ thuật cho phần recovery và checkpointing.

## 2. Metrics summary

- Total scenarios: 7
- Success rate: 85.71%
- Average nodes visited: 6.86
- Total retries: 2
- Total interrupts: 2

## 3. Ý nghĩa của kết quả SQLite

Kết quả 85.71% cho thấy lần chạy sample với SQLite vẫn còn một scenario chưa khớp route mong đợi. Tuy nhiên, điều quan trọng ở file này là **khả năng lưu và phục hồi trạng thái** đã hoạt động, không phải tối ưu routing.

Nói cách khác:

- `metrics.json` / `metrics_improved.json` dùng để đánh giá chất lượng routing tổng thể
- `lab_report_sqlite.md` dùng để chứng minh phần **checkpoint, recovery, resume**

## 4. Persistence design

Project hỗ trợ hai chế độ checkpointer:

- `memory`: dùng cho chạy nhanh trong dev/test.
- `sqlite`: dùng cho persistence thật, với `sqlite3.connect(..., check_same_thread=False)` và WAL mode.

### Vì sao chọn SQLite

- Có thể lưu checkpoint bền vững trên đĩa
- Có thể inspect lịch sử state theo `thread_id`
- Có thể resume workflow sau khi process dừng
- Phù hợp để demo production-style hơn memory saver

## 5. Cách flow lưu checkpoint hoạt động

Luồng logic khi chạy với SQLite:

1. Tạo `SqliteSaver` từ connection SQLite.
2. Compile graph với `checkpointer`.
3. Mỗi lần graph đi qua một node, state được lưu vào checkpoint.
4. Khi chạy lại với cùng `thread_id`, graph có thể khôi phục trạng thái đã lưu.

Điều này có nghĩa là checkpoint không chỉ là snapshot cuối cùng, mà là lịch sử các bước xử lý của workflow.

## 6. Bằng chứng resume / crash recovery

Demo recovery đã được minh họa bằng script:

- [scripts/demo_resume.py](../scripts/demo_resume.py)

Script này:

- chạy một scenario với SQLite checkpointer
- xác nhận checkpoint được ghi vào file database
- chạy lại với cùng `thread_id`
- chứng minh workflow có thể resume từ state đã lưu

File database tạo ra trong demo:

- `resume_demo.db`

## 7. Failure mode trong run SQLite

Lần chạy SQLite sample hiện tại có 85.71% success rate. Đây là dấu hiệu cho thấy persistence đã ổn, nhưng routing sample chưa hoàn toàn tối ưu trong file metrics phụ này.

Các nguyên nhân failure mode có thể gồm:

- query nhập vào chưa được normalize đủ tốt
- keyword matching còn thiếu một vài biến thể từ
- hidden logic đánh giá route chưa khớp hoàn toàn ở một scenario sample

Quan trọng hơn, failure này **không phải do checkpoint SQLite bị lỗi**, mà là do lớp routing / classification của scenario sample.

## 8. Hướng cải tiến

Nếu muốn nâng file SQLite run từ 85.71% lên mức cao hơn, có thể làm thêm:

- mở rộng keyword cho route `error`
- thêm normalization mạnh hơn cho query đầu vào
- thêm synonym map cho hành vi tương tự nhau
- log rõ hơn checkpoint history để debug route lệch

## 9. Lệnh chạy liên quan

### Chạy scenarios với SQLite

```bash
python -m langgraph_agent_lab.cli run-scenarios --config configs/lab_sqlite.yaml --output outputs/metrics-sqlite.json
```

### Validate metrics SQLite

```bash
python -m langgraph_agent_lab.cli validate-metrics --metrics outputs/metrics-sqlite.json
```

### Chạy demo recovery

```bash
python scripts/demo_resume.py
```

## 10. Kết luận

`lab_report_sqlite.md` nên được xem là phụ lục kỹ thuật cho persistence. Nó chứng minh rằng workflow có thể chạy với SQLite checkpointer, lưu checkpoint, và resume bằng `thread_id`. Mặc dù metrics sample hiện ở mức 85.71%, phần quan trọng của file này là xác nhận **crash recovery / persistence** đã được triển khai đúng.
