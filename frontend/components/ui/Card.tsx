import { HTMLAttributes, forwardRef } from 'react';
import { clsx } from 'clsx';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'paper';
  glow?: boolean;
  shimmer?: boolean;
}

const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = 'default', glow, shimmer, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={clsx(
          'card',
          {
            'card-elevated': variant === 'elevated',
            'card-paper': variant === 'paper',
            'silver-glow': glow,
            'shimmer': shimmer,
          },
          className
        )}
        data-content="card"
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';

export default Card;
