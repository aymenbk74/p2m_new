import { test, expect } from '@playwright/test';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const APP_URL = process.env.APP_URL || 'http://localhost:3000';

test.describe('Authentication Flow', () => {
  test('should create a new account and log in', async ({ page }) => {
    // Generate unique email for this test run
    const timestamp = Date.now();
    const testEmail = `test.user.${timestamp}@example.com`;
    const testPassword = 'TestPassword123!@#';
    const testName = 'Test User';
    const testAge = 25;
    const testCountry = 'Tunisia';
    const testGender = 'H';

    // Step 1: Navigate to the home page
    await page.goto(`${APP_URL}/`);
    await expect(page).toHaveTitle(/SmartShop|Home/i);

    // Step 2: Click on signup button (look for navigation or modal trigger)
    // Try to find and click signup link
    await page.click('button:has-text("CRÉER UN COMPTE"), a:has-text("CRÉER UN COMPTE"), [data-testid="signup-btn"]');
    
    // Wait for signup modal to appear
    await page.waitForSelector('.signup-luxury-box, .auth-modal-root');

    // Step 3: Fill in signup form
    await page.fill('input[name="first_name"]', testName);
    await page.fill('input[name="email"]', testEmail);
    await page.selectOption('select[name="gender"]', testGender);
    await page.fill('input[name="age"]', testAge.toString());
    await page.fill('input[name="country"]', testCountry);
    await page.fill('input[name="password"]', testPassword);

    // Step 4: Submit signup form
    await page.click('button:has-text("CONFIRMER L\'ADHÉSION")');

    // Step 5: Wait for success message
    await page.waitForSelector('.auth-message-luxury');
    const successMessage = await page.locator('.auth-message-luxury').textContent();
    expect(successMessage).toContain('Adhésion confirmée');

    // Step 6: Wait for redirect to login (auto-switch happens after 2 seconds)
    await page.waitForTimeout(2500);

    // Step 7: Verify we're on login screen
    await page.waitForSelector('.login-luxury-box, .auth-modal-root');
    await expect(page.locator('h2')).toContainText('CONNEXION');

    // Step 8: Fill in login form with the same credentials
    await page.fill('input[name="email"]', testEmail);
    await page.fill('input[name="password"]', testPassword);

    // Step 9: Submit login form
    await page.click('button:has-text("S\'IDENTIFIER")');

    // Step 10: Wait for successful login and redirect
    // After login, user should be redirected to /profile or /admin
    await page.waitForURL(/\/(profile|admin)/);
    
    // Verify we're logged in by checking localStorage
    const token = await page.evaluate(() => localStorage.getItem('token'));
    const userName = await page.evaluate(() => localStorage.getItem('userName'));
    
    expect(token).toBeTruthy();
    expect(userName).toBeTruthy();

    console.log(`✅ Test passed! Created account: ${testEmail}`);
    console.log(`   Token: ${token?.substring(0, 20)}...`);
    console.log(`   User: ${userName}`);
  });

  test('should fail login with incorrect credentials', async ({ page }) => {
    await page.goto(`${APP_URL}/`);
    
    // Open login modal
    await page.click('button:has-text("SE CONNECTER"), a:has-text("SE CONNECTER"), [data-testid="login-btn"]');
    
    // Wait for login modal
    await page.waitForSelector('.login-luxury-box, .auth-modal-root');

    // Fill with wrong credentials
    await page.fill('input[name="email"]', 'wrong@example.com');
    await page.fill('input[name="password"]', 'WrongPassword123!');

    // Submit
    await page.click('button:has-text("S\'IDENTIFIER")');

    // Check for error message
    await page.waitForSelector('.auth-error-luxury');
    const errorMessage = await page.locator('.auth-error-luxury').textContent();
    expect(errorMessage).toContain('Identifiants invalides');
  });
});
