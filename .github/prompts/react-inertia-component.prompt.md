---
mode: 'agent'
description: 'Create React + Inertia.js + TypeScript component with proper typing, useForm, Tailwind 4.'
---
# React + Inertia Component

## Rules
- Full TypeScript — no `any` type
- Small, focused components (single responsibility)
- Business logic outside JSX when possible
- Use `useForm` from `@inertiajs/react` for all mutations
- Reuse existing UI components (Headless UI + Tailwind)
- After creation — run multi-language-check

## Steps
1. Run delta-analysis — find similar existing components
2. Define TypeScript interface for props
3. Create component file in `resources/js/Components/` or `resources/js/Pages/`
4. Implement component with proper types
5. Use `useForm` for any form submissions
6. Add translations for all user-facing strings
7. Run multi-language-check

## Template
```tsx
interface Props {
  // define props here
}

export default function ComponentName({ prop }: Props) {
  const { data, setData, post, processing, errors } = useForm({
    field: '',
  });

  return (
    <div>
      {/* component */}
    </div>
  );
}
```
