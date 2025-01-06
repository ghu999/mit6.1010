(define y 10)
y
((lambda (z) (set! y (+ z y))) 9)
y
((lambda (z) (set! x (+ z y))) 9)
x
((lambda (y) ((lambda (z) (list y (set! y (+ 2 z)) y)) 7)) 4)
y
(define a 2)
(define b (set! a +))
(b 2 3)
(set! a 3)
(b a a)
