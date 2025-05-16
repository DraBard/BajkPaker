#!/usr/bin/env node

const { execSync } = require('child_process');
const path = require('path');

// Get workspace folder
const workspaceFolder = process.cwd();

console.log('Setting up MySQL database...');

try {
  // Stop and remove existing container if it exists
  console.log('Stopping any existing MySQL container...');
  try {
    execSync('docker rm -f bajkpaker-mysql', { stdio: 'inherit' });
  } catch (error) {
    // Ignore error if container doesn't exist
    console.log('No existing container found');
  }

  // Run new MySQL container
  console.log('Starting new MySQL container...');
  const command = `docker run --name bajkpaker-mysql -p 3306:3306 \
-e MYSQL_DATABASE=bajkpaker_dev \
-e MYSQL_USER=bajkpaker \
-e MYSQL_PASSWORD=BajkPaker93.83 \
-e MYSQL_ROOT_PASSWORD=BajkPaker93.83 \
-v ${workspaceFolder}/backend/database/init-scripts:/docker-entrypoint-initdb.d \
-d mariadb:10.6-focal`;

  execSync(command, { stdio: 'inherit' });
  
  console.log('MySQL container started successfully!');
  
  // Wait for MySQL to be ready
  console.log('Waiting for MySQL to be ready...');
  let ready = false;
  let attempts = 0;
  const maxAttempts = 30;
  
  while (!ready && attempts < maxAttempts) {
    try {
      execSync('docker exec bajkpaker-mysql mysqladmin ping -h localhost -u bajkpaker -pBajkPaker93.83', { stdio: 'ignore' });
      ready = true;
    } catch (error) {
      attempts++;
      console.log(`Waiting for MySQL to be ready... (${attempts}/${maxAttempts})`);
      // Wait 1 second before trying again
      execSync('sleep 1');
    }
  }
  
  if (ready) {
    console.log('MySQL is ready!');
  } else {
    console.error('MySQL failed to start within the expected time');
    process.exit(1);
  }
  
} catch (error) {
  console.error('Error setting up MySQL:', error.message);
  process.exit(1);
} 