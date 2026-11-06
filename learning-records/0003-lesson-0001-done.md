# Xong bài 0001: tự viết rule ABAC kết hợp RBAC; còn nhầm đường dẫn biến CEL

Người học tự giải thử thách của bài 0001: thêm `comment` vào rule `roles: [user]` có điều kiện `request.resource.attr.public == true`. `verify.py challenge` ĐẠT cả 6 dòng, nghĩa là không mở quyền quá tay cho `DAFFY_SECRET`. Quiz: câu 1, 2, 4 đúng ngay lần đầu. Câu 3 chọn `principal.attr.id` thay vì `request.principal.id`, tức là còn lẫn giữa `id` (field của principal) và `attr.*` (thuộc tính tuỳ ý).

**Evidence**: answers/0001-first-policy-quickstart.json; lab/policies/resource_album.yaml; output verify challenge mà người học dán vào.

**Implications**: Hỏi lại đường dẫn `request.principal.id` và `request.principal.attr.X` ở đầu bài 0002, cùng ba hiểu nhầm trong LR-0002.
