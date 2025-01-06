(begin
	(define (map func input)
		(if (equal? input ())
		()
		(cons (func (car input))       
            		(map func (cdr input)))))
	(define (filter func input)
  		(if (equal? input ())
		()
			(if (func (car input))
			(cons (car input) (filter func (cdr input)))
			(filter func (cdr input)))))
	(define (reduce func input initval)
		(if (equal? input ())
			initval
			(reduce func (cdr input) 
				(func initval (car input)))))
)
		