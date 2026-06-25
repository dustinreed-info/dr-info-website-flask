#!/usr/bin/env node

/**
 * S3/CloudFront Deployment Script
 * Usage: node scripts/deploy.js [bucket-name] [cloudfront-distribution-id]
 * Or set environment variables: S3_BUCKET, CLOUDFRONT_DIST_ID
 *
 * Builds the Astro site (npm run build) then syncs ./dist.
 */

import { execSync } from 'child_process';
import { existsSync, readFileSync } from 'fs';

const SOURCE_DIR = 'dist';

// Try to load .env file if it exists
if (existsSync('.env')) {
  console.log('Loading variables from .env file...');
  const envContent = readFileSync('.env', 'utf-8');
  envContent.split('\n').forEach((line) => {
    const trimmed = line.trim();
    if (trimmed && !trimmed.startsWith('#')) {
      const [key, ...valueParts] = trimmed.split('=');
      if (key && valueParts.length > 0) {
        const value = valueParts.join('=').trim();
        if (!process.env[key]) {
          process.env[key] = value;
        }
      }
    }
  });
}

const S3_BUCKET = process.argv[2] || process.env.S3_BUCKET;
const CLOUDFRONT_DIST_ID = process.argv[3] || process.env.CLOUDFRONT_DIST_ID;
const S3_REGION = process.env.S3_REGION || 'us-east-1';

if (!S3_BUCKET) {
  console.error('Error: S3 bucket name is required\n');
  console.log('Usage options:');
  console.log('  1. Command line: node scripts/deploy.js <bucket-name> [cloudfront-distribution-id]');
  console.log('  2. Environment variables: export S3_BUCKET=your-bucket-name');
  console.log('  3. .env file: Create .env with S3_BUCKET=your-bucket-name\n');
  console.log('Example .env file:');
  console.log('  S3_BUCKET=your-bucket-name');
  console.log('  CLOUDFRONT_DIST_ID=your-distribution-id');
  console.log('  S3_REGION=us-east-1');
  process.exit(1);
}

console.log('Starting deployment to S3/CloudFront\n');

try {
  console.log('Building static site (npm run build)...');
  execSync('npm run build', { stdio: 'inherit' });

  if (!existsSync(SOURCE_DIR)) {
    console.error(`Error: build did not produce "${SOURCE_DIR}" directory`);
    process.exit(1);
  }

  console.log(`Syncing ./${SOURCE_DIR} to S3 bucket: ${S3_BUCKET}`);
  execSync(
    `aws s3 sync ./${SOURCE_DIR} s3://${S3_BUCKET} --delete --region ${S3_REGION}`,
    { stdio: 'inherit' }
  );

  console.log('Setting correct content types and cache headers...');
  execSync(
    `aws s3 cp s3://${S3_BUCKET} s3://${S3_BUCKET} --recursive --region ${S3_REGION} --exclude "*" --include "*.html" --content-type "text/html; charset=utf-8" --metadata-directive REPLACE --cache-control "public, max-age=0, must-revalidate"`,
    { stdio: 'inherit' }
  );
  execSync(
    `aws s3 cp s3://${S3_BUCKET} s3://${S3_BUCKET} --recursive --region ${S3_REGION} --exclude "*" --include "*.css" --content-type "text/css; charset=utf-8" --metadata-directive REPLACE --cache-control "public, max-age=31536000, immutable"`,
    { stdio: 'inherit' }
  );
  execSync(
    `aws s3 cp s3://${S3_BUCKET} s3://${S3_BUCKET} --recursive --region ${S3_REGION} --exclude "*" --include "*.js" --content-type "application/javascript; charset=utf-8" --metadata-directive REPLACE --cache-control "public, max-age=31536000, immutable"`,
    { stdio: 'inherit' }
  );

  if (CLOUDFRONT_DIST_ID) {
    console.log('Creating CloudFront invalidation...');
    const invalidationId = execSync(
      `aws cloudfront create-invalidation --distribution-id ${CLOUDFRONT_DIST_ID} --paths "/*" --query 'Invalidation.Id' --output text`,
      { encoding: 'utf-8' }
    ).trim();

    console.log(`Invalidation created: ${invalidationId}`);
    console.log('Waiting for invalidation to complete...');

    execSync(
      `aws cloudfront wait invalidation-completed --distribution-id ${CLOUDFRONT_DIST_ID} --id ${invalidationId}`,
      { stdio: 'inherit' }
    );

    console.log('Invalidation completed!');
  } else {
    console.log('No CloudFront distribution ID provided, skipping invalidation');
  }

  console.log('\nDeployment complete!');
  console.log(`Site deployed to: s3://${S3_BUCKET} (region: ${S3_REGION})`);
  if (CLOUDFRONT_DIST_ID) {
    console.log(`CloudFront distribution: ${CLOUDFRONT_DIST_ID}`);
  }
} catch (error) {
  console.error('Deployment failed:', error.message);
  process.exit(1);
}
