pipeline {
  agent any

  environment {
    TF_IN_AUTOMATION = "true"
    TF_INPUT = "0"
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Verify Tooling') {
      steps {
        sh '''
          terraform version
          cosign version
          python3 --version
        '''
      }
    }

    stage('Provenance Verification') {
      steps {
        sh '''
          python3 -m venv .venv
          . .venv/bin/activate
          pip install .
          securetf verify main.tf --pubkey cosign.pub
        '''
      }
    }

    stage('Terraform Init') {
      steps {
        sh 'terraform init -no-color'
      }
    }

    stage('Terraform Plan') {
      steps {
        sh 'terraform plan -no-color'
      }
    }
  }
}

