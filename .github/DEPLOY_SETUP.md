# 🔄 Auto-Deploy to Hugging Face Setup

This repository includes GitHub Actions to automatically deploy your changes to Hugging Face Spaces.

## ⚙️ Setup Instructions

### 1. Create a Hugging Face Token

1. Go to [Hugging Face Settings > Tokens](https://huggingface.co/settings/tokens)
2. Click "New token"
3. Name it: `GitHub-Auto-Deploy`
4. Set role to: **Write**
5. Copy the token (starts with `hf_...`)

### 2. Add Token to GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `HF_TOKEN`
5. Value: Paste your Hugging Face token
6. Click **Add secret**

### 3. How It Works

The workflow will automatically:

- ✅ **Trigger on push** to `main` branch
- ✅ **Validate project structure** and Python syntax
- ✅ **Run basic import tests** to ensure code works
- ✅ **Deploy to Hugging Face** if everything passes
- ✅ **Provide deployment summary** with links and status

### 4. Manual Deployment

You can also trigger deployment manually:

1. Go to **Actions** tab in your GitHub repository
2. Select **Deploy to Hugging Face Spaces**
3. Click **Run workflow**
4. Optionally check "Force deployment" to deploy even without changes

### 5. Monitoring

- Check the **Actions** tab for deployment status
- View deployment logs for troubleshooting
- Your Hugging Face Space will update within a few minutes

### 🔗 Links

- **Hugging Face Space**: https://huggingface.co/spaces/abhash-chakraborty/text_extractor
- **Live App**: https://abhash-chakraborty-text-extractor.hf.space
- **GitHub Repository**: https://github.com/Abhash-Chakraborty/AI-Text-Extractor

### 🛠️ Troubleshooting

**Deployment fails?**
- Verify `HF_TOKEN` is set correctly in GitHub secrets
- Check token has **write** permissions
- Ensure Hugging Face Space exists and is accessible

**Changes not visible?**
- Hugging Face may take 2-5 minutes to rebuild the space
- Check the space logs on Hugging Face for any errors
- Verify the space is set to auto-rebuild on git push
