---
name: ATTP Hoang Giang Design System
colors:
  surface: '#f4fcf0'
  surface-dim: '#d5dcd1'
  surface-bright: '#f4fcf0'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff6ea'
  surface-container: '#e9f0e5'
  surface-container-high: '#e3eadf'
  surface-container-highest: '#dde5d9'
  on-surface: '#171d16'
  on-surface-variant: '#3e4a3d'
  inverse-surface: '#2b322b'
  inverse-on-surface: '#ecf3e7'
  outline: '#6e7b6c'
  outline-variant: '#bdcaba'
  surface-tint: '#006e2d'
  primary: '#006b2c'
  on-primary: '#ffffff'
  primary-container: '#00873a'
  on-primary-container: '#f7fff2'
  inverse-primary: '#62df7d'
  secondary: '#006d30'
  on-secondary: '#ffffff'
  secondary-container: '#92f5a4'
  on-secondary-container: '#007233'
  tertiary: '#a72d51'
  on-tertiary: '#ffffff'
  tertiary-container: '#c74668'
  on-tertiary-container: '#fffbff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#7ffc97'
  primary-fixed-dim: '#62df7d'
  on-primary-fixed: '#002109'
  on-primary-fixed-variant: '#005320'
  secondary-fixed: '#95f8a7'
  secondary-fixed-dim: '#79db8d'
  on-secondary-fixed: '#00210a'
  on-secondary-fixed-variant: '#005323'
  tertiary-fixed: '#ffd9de'
  tertiary-fixed-dim: '#ffb2bf'
  on-tertiary-fixed: '#3f0016'
  on-tertiary-fixed-variant: '#8a143c'
  background: '#f4fcf0'
  on-background: '#171d16'
  surface-variant: '#dde5d9'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.04em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 22px
    fontWeight: '700'
    lineHeight: 28px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 32px
  touch-target: 44px
  container-margin: 16px
  gutter: 12px
---

## Brand & Style
The design system is engineered for high-stakes food safety management (ISO 22000), prioritizing clarity, authority, and hygiene. The visual narrative balances a modern corporate aesthetic with a "clean-room" feel, evoking the sterile and organized nature of a food production facility.

The style is **Modern / Corporate**, utilizing a flat design language with subtle depth to differentiate actionable elements. High legibility in Vietnamese and generous whitespace ensure that critical data entry and safety checks are performed without cognitive overload. The interface focuses on reliability and professional trust, ensuring that compliance officers and factory staff feel supported by a robust, systematic tool.

## Colors
The color palette is anchored in shades of green to symbolize safety, compliance, and freshness. 

- **Primary Green (#16A34A)** is used for primary actions and brand presence.
- **Dark Green (#15803D)** provides contrast for active states and headers.
- **Background (#F6F8FA)** is a cool, clinical grey that reduces eye strain compared to pure white, while **Surface White (#FFFFFF)** is reserved for elevated cards and input fields to draw focus.
- **Semantic Colors** are strictly reserved for status: **Danger Red** for non-compliance or critical alerts, and **Success Green** for verified safety checks.

## Typography
This design system utilizes **Inter** for its exceptional legibility and neutral, systematic tone. The type scale is optimized for the Vietnamese language, ensuring diacritics are clear and do not clash with line heights.

- **Headlines:** Bold and tight for quick scanning of section titles and factory zones.
- **Body:** Standardized at 16px for optimal readability on mobile devices in factory environments.
- **Labels:** Used for metadata, timestamps, and status badges, often in uppercase or semi-bold to distinguish them from prose.

## Layout & Spacing
The layout follows a **Fluid Grid** model optimized for mobile-first interaction. 

- **Safe Zones:** A 16px horizontal margin is maintained on all screens.
- **Vertical Rhythm:** Built on a 4px baseline, with 16px as the standard spacing between related elements and 24px-32px between distinct sections.
- **Touch Targets:** All interactive elements (buttons, inputs, navigation items) must adhere to a minimum height of 44px to accommodate gloved or rapid use in a factory setting.
- **Navigation:** A fixed 56px height bottom bar provides persistent access to the three primary app modules.

## Elevation & Depth
The design system employs **Tonal Layers** combined with **Ambient Shadows** to create a functional hierarchy without visual clutter.

- **Level 0 (Background):** The base `#F6F8FA` surface.
- **Level 1 (Cards/Inputs):** White surfaces with a subtle 1px border (`#E2E8F0`) and a soft shadow (0px 2px 4px rgba(15, 23, 42, 0.05)).
- **Level 2 (Active States/Modals):** More pronounced shadows (0px 10px 15px -3px rgba(15, 23, 42, 0.1)) to draw immediate attention.
- **Headers:** The fixed top header uses a solid Primary Green fill with no shadow, acting as the structural anchor of the UI.

## Shapes
The shape language is friendly yet professional.
- **Standard Radius:** 14px-16px (`rounded-lg` or `rounded-xl`) for cards and primary containers to soften the industrial nature of the app.
- **Component Radius:** 8px for input fields and small buttons.
- **Status Badges:** Fully rounded (pill-shaped) to distinguish them from interactive buttons.

## Components
Consistent implementation of components ensures speed and accuracy during safety inspections:

- **Fixed Top Header:** Primary Green background, white text. Contains the current screen title (e.g., "Kiểm tra ATTP") and a profile/notif icon.
- **Fixed Bottom Navigation:** 3 tabs (e.g., Dashboard, Logs, Profile). Uses `secondary-text` for inactive states and `primary-green` for active states.
- **Action Cards:** Large, white cards with 16px radius. Used for launching inspections. Includes a prominent icon and a title.
- **Data Cards:** Compact cards for listing recent records. Uses a 2-column layout for "Time" and "Status".
- **Form Inputs:** 44px height, 8px radius, white background with a light grey border. Focus state uses a 2px Primary Green ring.
- **Status Banners:** Full-width or card-based banners. 
    - *Success:* Green text on `#ECFDF5`.
    - *Danger:* Red text on `#FEF2F2`.
- **Buttons:** 
    - *Primary:* Solid Green, white text, 8px radius.
    - *Secondary:* Ghost style with Primary Green border.