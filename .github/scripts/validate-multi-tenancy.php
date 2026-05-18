<?php
// .github/scripts/validate-multi-tenancy.php

require __DIR__ . '/../../vendor/autoload.php';
$app = require_once __DIR__ . '/../../bootstrap/app.php';
$app->make('Illuminate\Contracts\Console\Kernel')->bootstrap();

echo "🔐 Multi-Tenancy Validation\n";

$models = glob(app_path('Models/*.php'));

foreach ($models as $model) {
    $content = file_get_contents($model);
    $modelName = basename($model, '.php');
    
    if (strpos($content, 'business_id') !== false || strpos($content, 'tenant') !== false) {
        echo "✅ {$modelName} — has tenant awareness\n";
    } else {
        echo "⚠️  {$modelName} — no business_id found\n";
    }
}

echo "\nMulti-tenancy validation finished.\n";