import { Turnstile } from '@marsidev/react-turnstile';

interface TurnstileWrapperProps {
  onSuccess: (token: string) => void;
  onError?: () => void;
}

export function TurnstileWrapper({ onSuccess, onError }: TurnstileWrapperProps) {
  const siteKey = import.meta.env.VITE_TURNSTILE_SITE_KEY || '1x00000000000000000000AA';
  
  return (
    <Turnstile
      siteKey={siteKey}
      onSuccess={onSuccess}
      onError={onError}
      options={{
        theme: 'light',
        size: 'normal',
      }}
    />
  );
}
