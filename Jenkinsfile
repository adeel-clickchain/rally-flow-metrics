pipeline {
  agent { docker { image 'python:3-alpine' } }
  stage {
    stage('build') {
      steps {
        sh 'pip3 install -r requirements.txt'
        sh 'python3 run_metrics_report.py -t navigation -s 2019-09-16 -e 2019-09-22'
      }
    }
  }
}