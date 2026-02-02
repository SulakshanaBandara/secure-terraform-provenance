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

    stage('Setup securetf') {
      steps {
        sh '''
          python3 -m venv .venv
          . .venv/bin/activate
          pip install -U pip
          pip install .
        '''
      }
    }

    // -------------------------------
    // MAIN BRANCH: attest → verify
    // -------------------------------
    stage('Attest in CI (main only)') {
      when {
        branch 'main'
      }
      steps {
        withCredentials([
          file(credentialsId: 'COSIGN_KEY_FILE', variable: 'COSIGN_KEY_PATH'),
          string(credentialsId: 'COSIGN_PASSWORD', variable: 'COSIGN_PASSWORD')
        ]) {
          sh '''
            . .venv/bin/activate
            export COSIGN_PASSWORD="$COSIGN_PASSWORD"
            securetf attest main.tf --key "$COSIGN_KEY_PATH"
          '''
        }
      }
    }

    stage('Verify Provenance (main only)') {
      when {
        branch 'main'
      }
      steps {
        sh '''
          . .venv/bin/activate
          securetf verify main.tf --pubkey cosign.pub
        '''
      }
    }

    // -------------------------------
    // ALL BRANCHES: Terraform plan
    // -------------------------------
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

  post {
    success {
      archiveArtifacts artifacts: '*.attestation*.json', fingerprint: true
    }
  }
}

