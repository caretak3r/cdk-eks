from flask import Flask, render_template, request
import os
import subprocess
import threading

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        form_data = request.form
        env_vars = {
            'AWS_PROFILE': form_data.get('AWS_PROFILE'),
            'AWS_REGION': form_data.get('AWS_REGION'),
            'AWS_ACCOUNT_ID': form_data.get('AWS_ACCOUNT_ID'),
            'AWS_ECR_REPO_URL': form_data.get('AWS_ECR_REPO_URL'),
            'AWS_CERTIFICATE_ARN': form_data.get('AWS_CERTIFICATE_ARN'),
            'AWS_EKS_KMS_ARN': form_data.get('AWS_EKS_KMS_ARN'),
            'AWS_VPC_ID': form_data.get('AWS_VPC_ID'),
            'AWS_PRIVATE_SUBNET_IDS': form_data.get('AWS_PRIVATE_SUBNET_IDS'),
            'AWS_KMS_EKS_KEY_ARN': form_data.get('AWS_KMS_EKS_KEY_ARN'),
            'AWS_KMS_EFS_KEY_ARN': form_data.get('AWS_KMS_EFS_KEY_ARN'),
            'AWS_KMS_RDS_KEY_ARN': form_data.get('AWS_KMS_RDS_KEY_ARN')
        }
        os.environ.update(env_vars)
        threading.Thread(target=run_cdk).start()
        return 'CDK deployment started. Check logs for updates.'
    return render_template('index.html')

def run_cdk():
    process = subprocess.Popen(['cdk', 'deploy'], stdout=subprocess.PIPE)
    for line in iter(process.stdout.readline, b''):
        print(line.decode().strip())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
