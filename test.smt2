(set-logic QF_NRA)

(declare-fun pi () Real)
(assert (>= pi 3.141592653589793238461))
(assert (<= pi 3.141592653589793238463))

(declare-fun eps () Real)
(assert (>= eps 0.1))
(assert (<= eps 1))

(declare-fun k () Real)
(assert (= k 200))

(declare-fun k () Real)
(assert (= k 200))

(assert
   (not
    (<=
        (+
        (* (/
                1
                (*
                    2
                    pi
                    (pow (sqrt (/ 4 (* eps eps))) 3)
                    (sqrt (* 2 pi))))

            (integral (- k) k
            (lambda (z Real)
            (* (integral (- v0 k) z
            (lambda (y Real)
                (exp (- (/ (* (- y v0) (- y v0) eps eps)
                               (* 2 4))))))

            (integral (- u0 k) z
            (lambda (x Real)
                (*  (exp (- (/ (* (- x u0) (- x u0) eps eps)
                               (* 2 4))))

                    )))

                    (exp (- (/ (* z z eps eps)
                               (* 2 4))))

                    )

                    ))
            )))
        (/ 3 100)
        )
        (+
        (*
            (exp eps)
            (/
                1
                (*
                    2
                    pi
                    (pow (sqrt (/ 4 (* eps eps))) 3)
                    (sqrt (* 2 pi))))
            (integral (- k) k
            (lambda (z Real)
            (integral (- v1 k) z
            (lambda (y Real)
            (integral (- u1 k) z
            (lambda (x Real)
                (*  (exp (- (/ (* (- x u1) (- x u1) eps eps)
                               (* 2 4))))
                    (exp (- (/ (* (- y v1) (- y v1) eps eps)
                               (* 2 4))))
                    (exp (- (/ (* z z eps eps)
                               (* 2 4))))
                    ))))))))
        (/ 1 8)
        )
    )))

(check-sat) ; should be unsat
(exit)


(assert
   (not
    (<=
        (+
        (* (/
                1
                (*
                    2
                    pi
                    (pow (sqrt (/ 4 (* eps eps))) 3)
                    (sqrt (* 2 pi))))
            (integral (- k) k
            (lambda (z Real)
            (integral (- v0 k) z
            (lambda (y Real)
            (integral (- u0 k) z
            (lambda (x Real)
                (*  (exp (- (/ (* (- x u0) (- x u0) eps eps)
                               (* 2 4))))
                    (exp (- (/ (* (- y v0) (- y v0) eps eps)
                               (* 2 4))))
                    (exp (- (/ (* z z eps eps)
                               (* 2 4))))
                    ))))))))
        (/ 3 100)
        )
        (+
        (*
            (exp eps)
            (/
                1
                (*
                    2
                    pi
                    (pow (sqrt (/ 4 (* eps eps))) 3)
                    (sqrt (* 2 pi))))
            (integral (- k) k
            (lambda (z Real)
            (integral (- v1 k) z
            (lambda (y Real)
            (integral (- u1 k) z
            (lambda (x Real)
                (*  (exp (- (/ (* (- x u1) (- x u1) eps eps)
                               (* 2 4))))
                    (exp (- (/ (* (- y v1) (- y v1) eps eps)
                               (* 2 4))))
                    (exp (- (/ (* z z eps eps)
                               (* 2 4))))
                    ))))))))
        (/ 1 8)
        )
    )))

(check-sat) ; should be unsat
(exit)
