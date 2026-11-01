# 🚀 Deploy PromptCascade to Render.com

## ✅ Prerequisites

All deployment files are ready:
- ✅ `Procfile` - Start command configuration
- ✅ `runtime.txt` - Python version (3.11.9)
- ✅ `render.yaml` - Render-specific configuration
- ✅ `requirements.txt` - Dependencies (with gunicorn)

---

## 🎯 Deployment Steps

### **Step 1: Push to GitHub**

```bash
cd d:\project\prompt\PromptCascade

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Ready for Render deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/PromptCascade.git
git branch -M main
git push -u origin main
```

---

### **Step 2: Create Render Account**

1. Go to **https://render.com**
2. Click **"Get Started"** or **"Sign Up"**
3. Sign up with **GitHub** (recommended for easy integration)
4. **No credit card required** for free tier!

---

### **Step 3: Create Web Service**

1. Once logged in, click **"New +"** button (top right)
2. Select **"Web Service"**
3. Choose **"Build and deploy from a Git repository"**
4. Click **"Connect GitHub"** if not already connected
5. Find and select your **PromptCascade** repository
6. Click **"Connect"**

---

### **Step 4: Configure Service**

Fill in the settings:

**Basic Settings:**
- **Name:** `promptcascade` (or any name you prefer)
- **Region:** Choose closest to you (e.g., Oregon, Frankfurt)
- **Branch:** `main`
- **Root Directory:** *(leave blank)*

**Build & Deploy:**
- **Environment:** `Python 3`
- **Build Command:** 
  ```
  pip install -r requirements.txt
  ```
- **Start Command:**
  ```
  gunicorn --chdir frontend app:app --bind 0.0.0.0:$PORT
  ```

**Plan:**
- Select **"Free"** tier

---

### **Step 5: Environment Variables (Optional)**

Click **"Advanced"** → **"Add Environment Variable"** to add:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `PYTHON_VERSION` | `3.11.9` |

*(These are optional - defaults work fine)*

---

### **Step 6: Deploy**

1. Click **"Create Web Service"**
2. Render will start building your app
3. Watch the logs in real-time
4. Wait **3-5 minutes** for first deployment
5. Look for **"Your service is live 🎉"** message

---

### **Step 7: Access Your App**

Your app will be live at:
```
https://promptcascade.onrender.com
```
*(Replace `promptcascade` with your service name)*

**Pages available:**
- Home: `https://your-app.onrender.com/`
- Demo: `https://your-app.onrender.com/demo`
- Experiment: `https://your-app.onrender.com/experiment`
- Results: `https://your-app.onrender.com/results`

---

## 🎨 Custom Domain (Optional)

To use your own domain:

1. Buy a domain (e.g., from Namecheap, GoDaddy)
2. In Render dashboard, go to your service
3. Click **"Settings"** → **"Custom Domains"**
4. Click **"Add Custom Domain"**
5. Enter your domain: `promptcascade.com`
6. Add the CNAME record to your DNS:
   ```
   CNAME: www → your-app.onrender.com
   ```
7. Wait for DNS propagation (5-30 minutes)
8. SSL certificate will be auto-generated!

---

## 🔄 Auto-Deploy on Git Push

Once connected, Render automatically deploys when you push to GitHub:

```bash
# Make changes to your code
git add .
git commit -m "Update feature"
git push

# Render automatically detects and deploys!
```

---

## 📊 Render Free Tier Details

**What you get (FREE):**
- ✅ 750 hours/month (enough for 24/7)
- ✅ Automatic SSL certificate
- ✅ Custom domains
- ✅ Automatic deployments
- ✅ Environment variables
- ✅ Build & deploy logs

**Limitations:**
- ⚠️ Server spins down after **15 minutes** of inactivity
- ⚠️ First request after sleep takes **~30 seconds** to wake up
- ⚠️ 512 MB RAM
- ⚠️ Shared CPU

**For production use**, upgrade to paid plan ($7/month) for:
- No cold starts
- More RAM/CPU
- Faster performance

---

## 🔧 Troubleshooting

### **Build Fails**

**Check these:**
1. `requirements.txt` is present and valid
2. Python version in `runtime.txt` is supported
3. Build Command is correct: `pip install -r requirements.txt`
4. Check build logs for specific errors

**Common fixes:**
```bash
# Ensure all dependencies are listed
pip freeze > requirements.txt

# Check Python version compatibility
python --version
```

---

### **App Crashes / Won't Start**

**Check Start Command:**
```
gunicorn --chdir frontend app:app --bind 0.0.0.0:$PORT
```

**View logs:**
1. Go to Render dashboard
2. Select your service
3. Click "Logs" tab
4. Look for error messages

**Common issues:**
- Missing `$PORT` variable → Render provides this automatically
- Wrong path to app → Check `--chdir frontend`
- Missing gunicorn → Check `requirements.txt`

---

### **Cold Start Delay**

**This is normal on free tier!**

After 15 minutes of no traffic, the server sleeps. First request takes ~30 seconds.

**Solutions:**
1. **Upgrade to paid plan** ($7/month) - no cold starts
2. **Use a pinger service** - Keep app awake (not recommended)
3. **Accept the delay** - Fine for demos/portfolios

---

### **Port Issues**

Make sure you're using `$PORT` variable:
```bash
# Correct ✅
--bind 0.0.0.0:$PORT

# Wrong ❌
--bind 0.0.0.0:5000
```

Render assigns the port automatically via `$PORT` environment variable.

---

## 📝 Configuration Files Explained

### **Procfile**
```
web: gunicorn --chdir frontend app:app --bind 0.0.0.0:$PORT
```
Tells Render how to start your app.

### **runtime.txt**
```
python-3.11.9
```
Specifies Python version to use.

### **render.yaml** (Optional)
Infrastructure-as-code configuration. Allows deploying from GitHub without manual setup.

---

## 🧪 Test Before Deploying

Test with gunicorn locally:

```bash
# Install gunicorn (already done)
pip install gunicorn

# Run production server locally
gunicorn --chdir frontend app:app --bind 0.0.0.0:5000

# Visit http://localhost:5000
# If works locally, will work on Render!
```

---

## 📈 Monitor Your App

### **View Metrics:**
1. Go to Render dashboard
2. Select your service
3. View:
   - Request volume
   - Response times
   - Memory usage
   - CPU usage

### **View Logs:**
Real-time logs available in dashboard:
- Build logs
- Deploy logs
- Application logs

### **Set Up Alerts:**
Configure email notifications for:
- Deploy failures
- Service crashes
- High resource usage

---

## 🔐 Security Best Practices

### **Environment Variables:**
Never commit sensitive data. Use environment variables:

```bash
# Generate secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Add to Render dashboard:
SECRET_KEY=your-generated-key
```

### **HTTPS:**
Automatic with Render! All traffic is SSL encrypted.

### **Dependencies:**
Keep updated for security patches:
```bash
pip list --outdated
pip install --upgrade package-name
pip freeze > requirements.txt
```

---

## 🎯 Deployment Checklist

Before deploying:
- [x] Procfile created
- [x] runtime.txt created
- [x] render.yaml created
- [x] requirements.txt includes gunicorn
- [ ] Code pushed to GitHub
- [ ] GitHub repo is public (or Render has access)
- [ ] Render account created
- [ ] Web service configured
- [ ] App deployed successfully
- [ ] All pages accessible

After deployment:
- [ ] Test home page
- [ ] Test demo page
- [ ] Test experiment runner
- [ ] Test results viewer
- [ ] Check logs for errors
- [ ] Verify SSL certificate
- [ ] Share your URL!

---

## 📞 Support & Resources

**Render Documentation:**
- Flask Guide: https://render.com/docs/deploy-flask
- Environment Variables: https://render.com/docs/environment-variables
- Custom Domains: https://render.com/docs/custom-domains
- Troubleshooting: https://render.com/docs/troubleshooting

**Render Support:**
- Community Forum: https://community.render.com
- Status Page: https://status.render.com
- Support Email: support@render.com

**PromptCascade Docs:**
- Main README: `README.md`
- Running Guide: `HOW_TO_RUN.md`
- Frontend Guide: `FRONTEND_GUIDE.md`

---

## 🎉 Success!

Once deployed, share your app:

**Your PromptCascade is live at:**
```
https://your-app.onrender.com
```

**Demo page:**
```
https://your-app.onrender.com/demo
```

**Try it out and share with others!** 🚀

---

## 💡 Pro Tips

1. **Use descriptive service names** - Makes URLs cleaner
2. **Enable auto-deploy** - Pushes to GitHub deploy automatically
3. **Monitor logs** - Catch issues early
4. **Start with free tier** - Upgrade only when needed
5. **Use environment variables** - For configuration
6. **Add custom domain** - More professional
7. **Keep dependencies updated** - For security
8. **Document your deployment** - For future reference

---

## 🔄 Update Your Deployed App

After initial deployment:

```bash
# Make changes to your code
git add .
git commit -m "Add new feature"
git push origin main

# Render automatically:
# 1. Detects the push
# 2. Rebuilds the app
# 3. Deploys new version
# 4. No downtime!
```

---

## ✅ Deployment Complete!

**Your Flask app is now live on the internet!**

**Next steps:**
1. Test all functionality
2. Share your URL
3. Add to your portfolio
4. Monitor performance
5. Gather feedback

**Congratulations! 🎉**

---

**Questions?** Check Render docs or project documentation files.

**Issues?** Check the Troubleshooting section above.

**Ready to deploy? Follow Step 1!** 🚀
