---
mode: 'agent'
description: 'Implement business logic using the Laravel Action pattern — clean, reusable, testable.'
---
# Laravel Action Implementation

Use this for any non-trivial business operation (CreateLead, GenerateInvoice, SendNotification, etc.).

## Template

```php
<?php

namespace App\Actions\{Module};

use App\Models\{Model};
use App\DataTransferObjects\{Model}Data;

final class {ActionName}Action
{
    public function execute({Model}Data $data): {Model}
    {
        return DB::transaction(function () use ($data) {
            $model = {Model}::create($data->toArray());
            event(new {Model}Created($model));
            return $model;
        });
    }
}
```

## Steps
1. Run delta-analysis first
2. Create DTO if needed (`app/DataTransferObjects/`)
3. Create Action class (`app/Actions/{Module}/`)
4. Implement `execute()` method with proper typing
5. Wrap in DB transaction if needed
6. Fire events
7. Call Action from thin controller or Job
8. Write unit test for the Action
