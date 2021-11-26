sbcl --load quicklisp.lisp

(ql:quickload "cl-csv")
(defparameter input (cl-csv:read-csv #P"out.csv"))

(defparameter score ())
(loop for line in input
   do (push (nth 0 (with-input-from-string (in (nth 1 line))
  (loop for x = (read in nil nil) while x collect x))) score))

(defparameter times ())
(loop for line in input
   do (push (nth 0 (with-input-from-string (in (nth 2 line))
  (loop for x = (read in nil nil) while x collect x))) times))

(defparameter mean_time 0)
(setq mean_time (/ (apply '+ times) (length times)))

(defparameter mean_score 0)
(setq mean_score (/ (apply '+ score) (float (length score))))

(defparameter variance_score 0)
(setq variance_score (/ (apply '+ (mapcar (lambda (x) (* x x)) (mapcar (lambda (n) (- n mean_score))
        score))) (length score)))

mean_time
variance_score
