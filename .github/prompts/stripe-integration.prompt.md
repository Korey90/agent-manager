---
mode: 'agent'
description: 'Stripe payments, webhooks, subscriptions — secure integration with multi-tenancy.'
---
# Stripe Integration

## Rules
- Use official Stripe PHP SDK
- Secure webhook endpoints: CSRF disabled (`VerifyCsrfToken` exception) + signature verification
- Create dedicated Jobs for async processing (never process synchronously in webhook handler)
- Log all Stripe events
- Respect multi-tenancy — always scope to `business_id`

## Steps
1. Run delta-analysis first
2. Add route in `routes/api.php` (CSRF-exempt group)
3. Create webhook controller — verify signature first
4. Dispatch Job for async processing
5. Implement Job with idempotency check (store processed event IDs)
6. Log every event
7. Write test with mocked Stripe event

## Webhook controller template
```php
public function handle(Request $request): Response
{
    $payload = $request->getContent();
    $signature = $request->header('Stripe-Signature');

    try {
        $event = Webhook::constructEvent($payload, $signature, config('stripe.webhook_secret'));
    } catch (SignatureVerificationException $e) {
        return response('Invalid signature', 400);
    }

    ProcessStripeEvent::dispatch($event);

    return response('OK', 200);
}
```
