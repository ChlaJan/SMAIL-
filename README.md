# SMAIL---Email-client-for-elderly-users
This email client is adapted for mentally challenged users in the age group of 90 years and more. The developed email client is easy to use and contains only features that they may need.

## Getting started
Smail uses straightfoward and easy-to-use approach for control system. Control is based on big menu buttons and "CTRL+O" keyboard shortcut to show options menu.

For more detailed information read ReadME in [`smail`](https://github.com/ChlaJan/SMAIL-/tree/main/smail) folder

## Installation via Packages

### Step 1: Download installation package
Choose the right installation package for your operating system. 

Pre-built packages are available directly in the repository.
Download the package for your Linux distribution below:

| Distribution | Package |
|---|---|
| Debian / Ubuntu | [`smail_0.1.9_amd64.deb`](https://github.com/ChlaJan/SMAIL-/raw/main/smail_0.1.9_amd64.deb) |
| Fedora / RHEL | [`smail-0.1.9-1.fc43.x86_64.rpm`](https://github.com/ChlaJan/SMAIL-/raw/main/smail-0.1.9-1.fc43.x86_64.rpm) |

---


### Debian / Ubuntu (`.deb`)
```bash
# Navigate into the download directory 
cd Downloads

#Update repositories
sudo apt update

# Install packages
sudo dpkg -i smail_0.1.9 _amd64.deb
sudo apt install smail_0.1.9_amd64.deb
```

---

### Fedora / RHEL (`.rpm`)
```bash
# Navigate into the download directory 
cd Downloads

#Update repositories
sudo dnf update

# Install packages
sudo dnf install smail-0.1.9-1.fc43.x86_64.rpm
```

---

After installation, launch the app by running:
```bash
smail
```
> [!WARNING]
> On the first launch, the application will create a configuration file and close automatically.
> Please run `smail` a second time to start the application normally.

## Installation via Poetry
To get started with SMAIL, follow these steps to clone the repository and install dependencies:

### Step 1: Install Poetry
SMAIL uses Poetry for dependency management and packaging. 
If you don't have Poetry installed, you will need to install it first. 
You can follow this [step-by-step guide on how to install Poetry](https://gist.github.com/Isfhan/b8b104c8095d8475eb377230300de9b0).

### Step 2: Clone Repository and Install Dependencies
After installing Poetry, you can continue with the following steps:

```bash
# Clone project repository
git clone https://github.com/ChlaJan/SMAIL-

# Navigate into the project directory
cd SMAIL-

#navigate into smail directory
cd smail

# Build and install dependencies using Poetry
poetry build

poetry install

#start the application
poetry run smail
```

Supported Python Versions: This program is tested and optimized for Python 3.12.

#Installation demostration video 

https://github.com/user-attachments/assets/3e95f26c-bf7e-4e4f-b521-7b81df022682

