# Hiểu nhầm: "chưa có policy thì ALLOW", "'*' không gồm comment", và nhầm kind với action

Ba hiểu nhầm lộ ra trong các câu dự đoán của bài 0001 (ngày 2026-11-04):

1. Dự đoán rằng chưa có policy thì mọi thứ được ALLOW. Thực tế Cerbos mặc định DENY.
2. Cho rằng `comment` bị deny "vì chưa được định nghĩa", trong khi rule `actions: ['*']` khớp mọi action. Action là chuỗi tuỳ đặt, không phải khai báo ở đâu trước.
3. Gọi `album:object` là "action". Thực ra đó là `kind` của resource, dùng để chọn resource policy.

Phần suy luận về derived role `owner` (BUGS001 được phép vì `owner == principal.id`) là đúng, và kết luận DAFFY002 bị deny cũng đúng.

**Evidence**: answers/0001-first-policy-quickstart.json, câu `a-deny-all` và `b-owner`.

**Implications**: Dự đoán được ghi lại trước khi xem đáp án, nên đây là chẩn đoán thật, không phải lỗi gõ. Cần hỏi lại cả ba điểm ở đầu bài 0002 (truy xuất giãn cách), không nhắc trước. Khi dạy deny-by-default với `EFFECT_DENY` tường minh, nên đối chiếu với hiểu nhầm số 1. Status: chưa xác nhận đã sửa.

**Cập nhật (04:57):** Ở câu `c-daffy-comment` anh lập luận đúng rằng rule chỉ liệt kê `view:public` thì không áp dụng cho `comment`, tức là đã dùng đúng phép khớp action. Quiz-1 (mặc định deny) trả lời đúng ngay lần đầu, nhưng câu này làm ngay sau khi xem đáp án A, nên mới chỉ là fluency, chưa phải nhớ lâu. Vẫn phải hỏi lại ở bài 0002. Câu C còn một điểm chưa chính xác: anh nói "ai cũng xem được tài liệu có attribute public". Đúng ra là chỉ principal có role `user`, và chỉ khi `public == true` (xét giá trị, không phải "có thuộc tính"). Bài sau cần luyện phân biệt RBAC (`roles`) với điều kiện ABAC (`condition`).
