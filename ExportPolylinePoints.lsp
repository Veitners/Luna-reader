(defun c:ExportPolylinePoints ( / plObj interval dist points startPt relPoints filePath fileHandle row)
  (vl-load-com)

  ;; Prompt user to select a polyline
  (setq plObj (car (entsel "\nSelect a polyline: ")))
  (if (not (and plObj (eq (cdr (assoc 0 (entget plObj))) "LWPOLYLINE")))
    (progn
      (princ "\nSelected object is not a polyline or selection failed.")
      (exit)
    )
  )

  ;; Prompt user for interval distance
  (setq interval (getreal "\nEnter interval distance (in mm): "))
  (if (or (not interval) (<= interval 0))
    (progn
      (princ "\nInvalid interval distance.")
      (exit)
    )
  )

  ;; Initialize variables
  (setq dist 0
        points '()
        startPt (vlax-curve-getPointAtDist plObj 0))

  ;; Calculate points along the polyline
  (while (< dist (vlax-curve-getDistAtParam plObj (vlax-curve-getEndParam plObj)))
    (setq points (cons (vlax-curve-getPointAtDist plObj dist) points))
    (setq dist (+ dist interval))
  )

  ;; Reverse points list to maintain order
  (setq points (reverse points))

  ;; Calculate relative coordinates
  (setq relPoints
        (mapcar
          (function
            (lambda (pt)
              (list (- (car pt) (car startPt)) (- (cadr pt) (cadr startPt)))
            )
          )
          points
        )
  )

  ;; Set file path for CSV
  (setq filePath (strcat (getvar "DWGPREFIX") "PolylinePoints.csv"))

  ;; Open file for writing
  (setq fileHandle (open filePath "w"))
  (if (not fileHandle)
    (progn
      (princ "\nFailed to create the CSV file. Check file permissions.")
      (exit)
    )
  )

  ;; Write separator line
  (write-line "sep = ," fileHandle)

  ;; Write headers
  (write-line "Point Number,X Coordinate,Y Coordinate" fileHandle)

  ;; Write points to CSV
  (setq row 1)
  (foreach pt relPoints
    (write-line (strcat (itoa row) "," (rtos (car pt) 2 6) "," (rtos (cadr pt) 2 6)) fileHandle)
    (setq row (1+ row))
  )

  ;; Close the file
  (close fileHandle)

  ;; Notify user of success
  (princ (strcat "\nExported points to: " filePath))

  (princ)
)
