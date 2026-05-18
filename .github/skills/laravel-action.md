# Skill: Laravel Action Implementation

**Description:** Create clean, reusable business logic using Action pattern.

**When to use:** Any non-trivial business operation (CreateLead, GenerateInvoice, SendProjectNotification, etc.).

**Template:**
```php
<?php

namespace App\Actions\Leads;

use App\Models\Lead;
use App\DataTransferObjects\LeadData;

final class CreateLeadAction
{
    public function execute(LeadData $data): Lead
    {
        // business logic, events, transactions
        return DB::transaction(function () use ($data) {
            $lead = Lead::create($data->toArray());
            event(new LeadCreated($lead));
            return $lead;
        });
    }
}