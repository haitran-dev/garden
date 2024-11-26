## I'm quite curious about technique behind this

> [!INFO] If you sincerely want to know, I am willing to answer.
> Kỹ thuật được sử dụng ở đây bao gồm 3 điểm chính
> - Một list item sử dụng flex (cần lưu ý không có gap giữa các items)
> - Một pseudo element (:before) của flex container element để tạo hiệu ứng background khi hover
> - Tính năng CSS mới **anchor** và **anchor-size** cho phép bạn định vị (position) background element một cách tương đối (relatively) theo các hovered element được ["neo giữ"](https://developer.chrome.com/blog/anchor-positioning-api) với thuộc tính anchor (giống như việc lưu 1 element vào 1 variable)

## How does it work ?

### Horizontal
![[Screen Recording 2024-11-10 at 15.43.26.mov]]
### Vertical
![[Screen Recording 2024-11-10 at 15.47.28.mov]]

### Refs
- https://developer.chrome.com/blog/anchor-positioning-api
- https://developer.mozilla.org/en-US/docs/Web/CSS/anchor
- https://developer.mozilla.org/en-US/docs/Web/CSS/anchor-size