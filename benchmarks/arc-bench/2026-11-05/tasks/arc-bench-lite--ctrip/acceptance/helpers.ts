import { expect, type Page, type Locator } from '@playwright/test';

import { ACCOUNTS, BENCHMARK_NOW, IDS } from './fixtures/data';
export { ACCOUNTS, IDS };
type Scope = Page | Locator;
export const field = (s: Scope, name: string) => s.getByLabel(name, { exact: true });
export const button = (s: Scope, name: string) => s.getByRole('button', { name, exact: true });
export const action = (s: Scope, name: string) => button(s, name).or(s.getByRole('link', { name, exact: true }));
export const region = (s: Scope, name: string) => s.getByRole('region', { name, exact: true });
export const dialog = (s: Scope, name: string) => s.getByRole('dialog', { name, exact: true });
export const tab = (s: Scope, name: string) => s.getByRole('tab', { name, exact: true });
export const radio = (s: Scope, name: string) => s.getByRole('radio', { name, exact: true });
export const checkbox = (s: Scope, name: string) => s.getByRole('checkbox', { name, exact: true });
export const nav = (page: Page) => page.getByRole('navigation', { name: 'Global navigation', exact: true });
// The three alternatives expose the same public business-record contract.
export const record = (s: Scope, name: string) => s.getByRole('listitem', { name: `Record ${name}`, exact: true })
  .or(s.getByRole('row', { name: `Record ${name}`, exact: true })).or(s.getByRole('group', { name: `Record ${name}`, exact: true }));
// Count only publicly named business records, not nested decorative lists or table headers.
export const records = (s: Scope) => s.getByRole('listitem', { name: /^Record / })
  .or(s.getByRole('row', { name: /^Record / })).or(s.getByRole('group', { name: /^Record / }));
export const flight = (page: Page, number: string) => region(page, 'Flight list').getByRole('listitem', { name: `Flight ${number}`, exact: true });
export const visible = async (l: Locator) => { await expect(l).toBeVisible(); };
export const heading = async (page: Page, name: string) => visible(page.getByRole('heading', { name, exact: true }));
export const textVisible = async (s: Scope, text: string) => {
  // Text may repeat within a record (for example route city and bus stop).
  // Presence is scoped to the semantic region and only visible copies count.
  const matches = s.getByText(text, { exact: true }).filter({ visible: true });
  await expect.poll(() => matches.count()).toBeGreaterThan(0);
  for (const match of await matches.all()) await expect(match).toBeVisible();
};
export const alertText = async (s: Scope, text: string) => { await expect(s.getByRole('alert').filter({ hasText: text })).toBeVisible(); };
export const total = async (page: Page, n: number) => textVisible(region(page, 'Fee breakdown'), `Order total: ¥${n}`);
export async function openHome(page: Page) {
  await page.goto('/');
}
export async function installClock(page: Page) { await page.clock.install({ time: new Date(BENCHMARK_NOW) }); }
export async function openLogin(page: Page) { await nav(page).getByRole('link', { name: 'Log in', exact: true }).click(); }
export async function login(page: Page, account: string, password = 'Travel1234') {
  await openLogin(page);
  await field(page, 'Account').fill(account);
  await field(page, 'Password').fill(password);
  await checkbox(page, 'Agree to terms').check();
  await button(page, 'Log in').click();
  await visible(action(page, 'My account'));
}
export async function loginOwner(page: Page, owner: string) {
  const a = ACCOUNTS[owner];
  if (!a?.email || !a.password) throw new Error(`No password-login fixture for ${owner}`);
  await login(page, a.email, a.password);
}
export async function signedOut(page: Page) {
  await visible(nav(page).getByRole('link', { name: 'Log in', exact: true }));
  await expect(action(page, 'My account')).toHaveCount(0);
}
export async function chooseDate(page: Page, label: string, date: string) { await field(page, label).click(); await button(page, date).click(); }
export async function searchFlights(page: Page, origin = 'Chengdu', destination = 'Guangzhou', date = '2026-07-21') {
  await field(page, 'Origin').fill(origin);
  await field(page, 'Destination').fill(destination);
  await chooseDate(page, 'Departure date', date);
  await button(page, 'Search flights').click();
  await visible(region(page, 'Flight list'));
}
export async function flightOrder(page: Page) {
  const entries = region(page, 'Flight list').getByRole('listitem');
  const result: string[] = [];
  // Reading ordered identities is the sorting oracle, not a position-based action locator.
  for (const item of await entries.all()) {
    const snapshot = await item.ariaSnapshot();
    const m = snapshot.match(/^[- ]*listitem "Flight ([A-Z]+[0-9]+)"/m);
    if (!m) throw new Error(`Missing public Flight identity: ${snapshot}`);
    result.push(m[1]);
  }
  return result;
}
export async function openBooking(page: Page) {
  await searchFlights(page);
  await button(flight(page, 'JD5162'), 'Show fares').click();
  await button(flight(page, 'JD5162').getByRole('group', { name: 'Economy fare', exact: true }), 'Book').click();
  await heading(page, 'Book flight');
}
export async function submitBooking(page: Page) {
  await field(region(page, 'Passenger details'), 'Full name').fill('Wang Wu');
  await field(region(page, 'Passenger details'), 'ID number').fill(IDS[0]);
  await field(page, 'Contact mobile').fill('13800000014');
  await checkbox(page, 'Agree to booking terms').check();
  await button(page, 'Submit order').click();
}
export async function openOrders(page: Page, owner: string) { await loginOwner(page, owner); await button(page, 'My account').click(); await page.getByRole('link', { name: 'Orders', exact: true }).click(); }
export async function openOrderDetails(page: Page, owner: string, number: string) { await openOrders(page, owner); await button(record(region(page, 'Order list'), number), 'View details').click(); }

export async function countdownSeconds(timer: Locator) {
  const text = await timer.innerText();
  const match = text.match(/(?:^|\s)(\d{1,3}):(\d{2})(?::(\d{2}))?(?:$|\s)/);
  if (!match) throw new Error(`Time remaining must render a duration: ${text}`);
  return match[3] ? Number(match[1]) * 3600 + Number(match[2]) * 60 + Number(match[3])
    : Number(match[1]) * 60 + Number(match[2]);
}
