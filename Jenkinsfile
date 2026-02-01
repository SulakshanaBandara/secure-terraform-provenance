pipeline {
  agent any

  environment {
    TF_IN_AUTOMATION = "true"
    TF_INPUT = "0"
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
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

    // Phase 2: CI becomes the signer (only main branch)
    stage('Attest in CI (main only)') {
      when { branch 'main' }
      steps {
        withCredentials([
          file(credentialsId: 'COSIGN_KEY_FILE', variable: 'COSIGN_KEY_PATH'),
          string(credentialsId: 'COSIGN_PASSWORD', variable: 'COSIGN_PASSWORD')
        ]) {
          sh '''
            . .venv/bin/activate

            # COSIGN reads password from env var automatically
            export COSIGN_PASSWORD="$COSIGN_PASSWORD"

            securetf attest main.tf --key "$COSIGN_KEY_PATH" --policy policy.yml
          '''
        }
      }
    }

    stage('Provenance Verification (hard gate)') {
      steps {
        sh '''
          . .venv/bin/activate
          securetf verify main.tf --pubkey cosign.pub --policy policy.ci.yml
        '''
      }
    }

    stage('Terraform Init') {
      steps { sh 'terraform init -no-color' }
    }

    stage('Terraform Plan') {
      steps { sh 'terraform plan -no-color' }
    }
  }
}

