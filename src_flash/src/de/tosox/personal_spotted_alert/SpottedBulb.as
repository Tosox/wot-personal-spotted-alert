package de.tosox.personal_spotted_alert
{
   import flash.display.DisplayObject;
   import flash.display.MovieClip;
   import flash.display.Sprite;
   import flash.events.Event;
   import flash.geom.Point;
   import flash.geom.Rectangle;
   import flash.utils.getDefinitionByName;

   // Inserted into a VehicleMarker through its vanilla insertSymbol and driven
   // from Python through callInsertedSymbolMethod. It wraps the vanilla target
   // designator bulb and pins it to the left of the marker's health bar
   public class SpottedBulb extends Sprite
   {
      // Lives in battleVehicleMarkers.swf, which the markers movie always loads
      private static const BULB_CLASS:String = "VehicleTargetDesignatorUI";

      // Anchors in order of preference; the health bar can be hidden in settings
      private static const ANCHOR_NAMES:Array = ["healthBar", "hpField"];

      private var _bulb:MovieClip = null;
      private var _layoutY:Number = 0;
      private var _offsetX:Number = 0;
      private var _offsetY:Number = 0;
      private var _anchoring:Boolean = false;

      public function SpottedBulb()
      {
         super();
         mouseEnabled = false;
         mouseChildren = false;
         var bulbClass:Class = getDefinitionByName(BULB_CLASS) as Class;
         this._bulb = new bulbClass() as MovieClip;
         // Without the frame scripts the hide animation loops back into view
         Object(this._bulb).setupFrameEvents();
         addChild(this._bulb);
         addEventListener(Event.REMOVED_FROM_STAGE, this.onRemovedFromStageHandler);
      }

      // The marker stacks its parts by height and y. Reporting no height and
      // keeping the stack's y apart from our own leaves its layout untouched
      override public function get height() : Number
      {
         return 0;
      }

      override public function get y() : Number
      {
         return this._layoutY;
      }

      override public function set y(value:Number) : void
      {
         this._layoutY = value;
      }

      // Offset of the bulb's centre from the anchor's left edge and vertical centre
      public function setLayout(offsetX:Number, offsetY:Number, scale:Number) : void
      {
         this._offsetX = offsetX;
         this._offsetY = offsetY;
         this._bulb.scaleX = this._bulb.scaleY = scale;
         this.updatePosition();
      }

      public function setColor(colorName:String, rgb:uint) : void
      {
         Object(this._bulb).setEffectColor(colorName, rgb);
      }

      public function show() : void
      {
         // No countdown, not a one-shot, play the show animation
         Object(this._bulb).showEffectTimer(0, false, false, true);
         this.startAnchoring();
      }

      public function hide() : void
      {
         Object(this._bulb).hideEffectTimer(true);
      }

      public function dispose() : void
      {
         this.stopAnchoring();
         removeEventListener(Event.REMOVED_FROM_STAGE, this.onRemovedFromStageHandler);
         if(this._bulb != null)
         {
            Object(this._bulb).dispose();
            removeChild(this._bulb);
            this._bulb = null;
         }
      }

      // The health bar moves when the player toggles the extended marker info,
      // so follow it every frame for as long as the bulb is on screen
      private function startAnchoring() : void
      {
         this.updatePosition();
         if(!this._anchoring)
         {
            this._anchoring = true;
            addEventListener(Event.ENTER_FRAME, this.onEnterFrameHandler);
         }
      }

      private function stopAnchoring() : void
      {
         if(this._anchoring)
         {
            this._anchoring = false;
            removeEventListener(Event.ENTER_FRAME, this.onEnterFrameHandler);
         }
      }

      private function updatePosition() : void
      {
         var anchor:DisplayObject = this.findAnchor();
         if(anchor == null)
         {
            return;
         }
         var bounds:Rectangle = this.getAnchorBounds(anchor);
         super.x = bounds.left + this._offsetX;
         super.y = bounds.top + bounds.height / 2 + this._offsetY;
      }

      // The health bar's own bounds also cover its hit splash and shine/glitch
      // effects, which come and go, so they would drag the bulb around. Its bar
      // always starts at local x 0, and only the bar clip itself is measured
      private function getAnchorBounds(anchor:DisplayObject) : Rectangle
      {
         var bar:DisplayObject = null;
         try
         {
            bar = Object(anchor).healthBar as DisplayObject;
         }
         catch(e:Error)
         {
            bar = null;
         }
         if(bar == null)
         {
            return anchor.getBounds(parent);
         }
         var bounds:Rectangle = bar.getBounds(parent);
         bounds.left = parent.globalToLocal(anchor.localToGlobal(new Point(0, 0))).x;
         return bounds;
      }

      private function findAnchor() : DisplayObject
      {
         if(parent == null)
         {
            return null;
         }
         for each(var name:String in ANCHOR_NAMES)
         {
            var candidate:DisplayObject = null;
            try
            {
               candidate = parent[name] as DisplayObject;
            }
            catch(e:Error)
            {
               candidate = null;
            }
            if(candidate != null && candidate.visible)
            {
               return candidate;
            }
         }
         return null;
      }

      private function onEnterFrameHandler(event:Event) : void
      {
         // The bulb hides itself once its hide animation has played out
         if(this._bulb == null || !this._bulb.visible)
         {
            this.stopAnchoring();
            return;
         }
         this.updatePosition();
      }

      // A marker disposes its inserted parts without calling dispose on them
      private function onRemovedFromStageHandler(event:Event) : void
      {
         this.stopAnchoring();
      }
   }
}
