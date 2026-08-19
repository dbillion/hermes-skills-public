#!/usr/bin/env node

/**
 * Mermaid Diagram Generator Helper
 * Scans for .mmd files and generates SVG/PNG using Mermaid CLI (mmdc).
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const diagramDir = path.join(process.cwd(), 'docs', 'diagrams');

function ensureDirectoryExistence(filePath) {
  const dirname = path.dirname(filePath);
  if (fs.existsSync(dirname)) return true;
  fs.mkdirSync(dirname, { recursive: true });
}

function generateDiagrams() {
  if (!fs.existsSync(diagramDir)) {
    console.log(`No diagrams found at ${diagramDir}`);
    return;
  }

  const files = fs.readdirSync(diagramDir).filter(f => f.endsWith('.mmd'));
  
  if (files.length === 0) {
    console.log('No .mmd files found.');
    return;
  }

  console.log(`Found ${files.length} diagrams. Generating...`);

  files.forEach(file => {
    const inputPath = path.join(diagramDir, file);
    const outputSvgPath = path.join(diagramDir, file.replace('.mmd', '.svg'));
    
    try {
      console.log(`Processing ${file}...`);
      execSync(`mmdc -i "${inputPath}" -o "${outputSvgPath}" -w 1200`, { stdio: 'inherit' });
      console.log(`✅ Generated ${path.basename(outputSvgPath)}`);
    } catch (error) {
      console.error(`❌ Failed to generate diagram for ${file}:`, error.message);
    }
  });
}

if (process.argv.includes('--test')) {
  console.log('Mermaid Helper Test Mode');
  try {
    const version = execSync('mmdc --version').toString().trim();
    console.log(`mmdc version: ${version}`);
    process.exit(0);
  } catch (e) {
    console.error('mmdc not found in PATH');
    process.exit(1);
  }
}

generateDiagrams();
