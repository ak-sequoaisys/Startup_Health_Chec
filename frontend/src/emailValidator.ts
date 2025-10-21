/**
 * Email validation utility to reject free email providers.
 */

const FREE_EMAIL_DOMAINS = new Set([
  "gmail.com",
  "googlemail.com",
  
  "yahoo.com",
  "yahoo.com.au",
  "yahoo.co.uk",
  "yahoo.ca",
  "yahoo.co.in",
  "ymail.com",
  "rocketmail.com",
  
  "outlook.com",
  "outlook.com.au",
  "hotmail.com",
  "hotmail.com.au",
  "hotmail.co.uk",
  "live.com",
  "live.com.au",
  "msn.com",
  
  "aol.com",
  "aol.com.au",
  
  "icloud.com",
  "me.com",
  "mac.com",
  
  "protonmail.com",
  "proton.me",
  "pm.me",
  
  "mail.com",
  "gmx.com",
  "gmx.net",
  "zoho.com",
  "yandex.com",
  "fastmail.com",
  "tutanota.com",
  "tutamail.com",
  "mailinator.com",
  "guerrillamail.com",
  "temp-mail.org",
  "10minutemail.com",
  "throwaway.email",
]);

/**
 * Check if an email address uses a free email provider domain.
 */
export function isFreeEmail(email: string): boolean {
  if (!email || !email.includes("@")) {
    return false;
  }
  
  const domain = email.split("@")[1]?.toLowerCase();
  return FREE_EMAIL_DOMAINS.has(domain);
}

/**
 * Validate that an email is a business email (not a free provider).
 * Returns an error message if invalid, or null if valid.
 */
export function validateBusinessEmail(email: string): string | null {
  if (!email) {
    return "Email is required";
  }
  
  if (!email.includes("@")) {
    return "Please enter a valid email address";
  }
  
  if (isFreeEmail(email)) {
    const domain = email.split("@")[1];
    return `Please use a business email address. Free email providers like ${domain} are not accepted.`;
  }
  
  return null;
}
