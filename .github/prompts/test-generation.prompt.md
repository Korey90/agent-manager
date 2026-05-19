---
mode: 'agent'
description: 'Generate PHPUnit 12 and Vitest tests for business logic, authorization, and multi-tenancy.'
---
# Test Generation

## Rules
- Test critical business paths (Actions, Services)
- Test authorization (Policies — both allowed and denied cases)
- Test multi-language where applicable
- Always run tests after implementation
- Use factories and seeders for test data
- Never test implementation details — test behavior

## Steps
1. Identify what needs testing (Action, Controller, Component)
2. Write PHPUnit test for backend logic (`tests/Feature/` or `tests/Unit/`)
3. Write Vitest test for React components (`tests/js/`)
4. Include authorization test cases
5. Include multi-tenancy isolation test (one business cannot access another's data)
6. Run `php artisan test` and `npm run test`

## PHPUnit template
```php
test('action does X when Y', function () {
    $business = Business::factory()->create();
    $user = User::factory()->for($business)->create();

    $result = (new SomeAction())->execute($data);

    expect($result)->toBeInstanceOf(Model::class);
});
```
