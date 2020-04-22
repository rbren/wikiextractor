NUM_JOBS=20
MAX_JOB=$(( NUM_JOBS - 1 ))
for i in $(seq 0 $MAX_JOB)
do
  cat ./deploy/tmpl-job.yaml \
    | sed "s/\$ID_MODULUS/$NUM_JOBS/g" \
    | sed "s/\$ID_RESIDUE/$i/g" \
    | sed "s/\$MS_PASSWORD/$MS_PASSWORD/g" \
    | sed "s/\$MS_USER/$MS_USER/g" \
    | sed "s/\$MS_HOST/$MS_HOST/g" \
    | sed "s/\$MS_DATABASE/$MS_DATABASE/g" \
    > ./deploy/jobs/job-$i.yaml
done
